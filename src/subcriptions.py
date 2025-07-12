"""
Subscription Manager for The Finisher.

This module provides a robust, scalable subscription system for managing user plans,
billing cycles, and payment processing, designed for enterprise-grade monetization.
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, ValidationError
import yaml
import os
from enum import Enum
import uuid
from retry import retry

# Configure logging for analytics and operational insights
logging.basicConfig(
    filename='subscription_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load configuration from environment variables or YAML for flexible deployment
CONFIG_FILE = os.getenv('SUBSCRIPTION_CONFIG', 'subscription_config.yaml')
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f) or {}
except FileNotFoundError:
    config = {}
    logging.warning("Configuration file not found, using default settings")

# Constants for subscription plans and settings
PLAN_CYCLES = config.get('PLAN_CYCLES', {
    "monthly": {"duration": timedelta(days=30), "price": 9.99},
    "bi-weekly": {"duration": timedelta(days=14), "price": 5.99},
    "yearly": {"duration": timedelta(days=365), "price": 99.99}
})
GRACE_PERIOD_DAYS = config.get('GRACE_PERIOD_DAYS', int(os.getenv('GRACE_PERIOD_DAYS', 7)))
MAX_PAYMENT_RETRIES = config.get('MAX_PAYMENT_RETRIES', int(os.getenv('MAX_PAYMENT_RETRIES', 3)))
DEFAULT_CURRENCY = config.get('DEFAULT_CURRENCY', os.getenv('DEFAULT_CURRENCY', 'USD'))

# Enum for subscription status
class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

# Pydantic model for subscription validation
class SubscriptionData(BaseModel):
    user_id: int = Field(..., gt=0)
    plan_type: str = Field(..., pattern=f"^(?:{'|'.join(PLAN_CYCLES.keys())})$")
    payment_date: datetime = Field(...)
    auto_pay: bool = Field(default=True)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    discount_code: Optional[str] = Field(default=None, max_length=50)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Subscription:
    """Manages user subscriptions with robust billing and status tracking for revenue generation."""
    
    def __init__(self, user_id: int, plan_type: str, payment_date: datetime, auto_pay: bool = True):
        """
        Initialize a subscription with validated data and unique ID.
        
        Args:
            user_id (int): Unique identifier for the user.
            plan_type (str): Type of subscription plan (e.g., monthly, yearly).
            payment_date (datetime): Date of last payment.
            auto_pay (bool): Whether auto-payment is enabled.
        """
        self.subscription_id = str(uuid.uuid4())  # Unique subscription ID
        try:
            self.data = SubscriptionData(
                user_id=user_id,
                plan_type=plan_type.lower(),
                payment_date=payment_date,
                auto_pay=auto_pay
            )
            self.next_payment_date = self.calculate_next_payment()
            self.trial_end_date = None  # For trial period tracking
            logging.info(f"Subscription {self.subscription_id} created for user {user_id} (plan: {plan_type})")
        except ValidationError as e:
            logging.error(f"Invalid subscription data: {e}")
            raise ValueError(f"Invalid subscription data: {e}")

    def calculate_next_payment(self) -> datetime:
        """
        Calculate the next payment date based on plan type, ensuring predictable billing cycles.
        
        Returns:
            datetime: Next payment date.
        """
        if self.data.plan_type in PLAN_CYCLES:
            return self.data.payment_date + PLAN_CYCLES[self.data.plan_type]["duration"]
        logging.error(f"Invalid plan type: {self.data.plan_type}")
        raise ValueError("Invalid subscription plan")

    def apply_discount(self, discount_code: str, discount_percentage: float) -> bool:
        """
        Apply a discount to the subscription, supporting promotional campaigns.
        
        Args:
            discount_code (str): Discount code to apply.
            discount_percentage (float): Percentage discount (0-100).
            
        Returns:
            bool: True if discount applied successfully, False otherwise.
        """
        try:
            if not 0 <= discount_percentage <= 100:
                logging.error(f"Invalid discount percentage: {discount_percentage}")
                return False
            self.data.discount_code = discount_code
            self.data.metadata["discount_applied"] = {
                "code": discount_code,
                "percentage": discount_percentage,
                "applied_at": datetime.utcnow().isoformat()
            }
            logging.info(f"Discount {discount_code} ({discount_percentage}%) applied to subscription {self.subscription_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to apply discount: {e}")
            return False

    def start_trial(self, trial_days: int) -> bool:
        """
        Start a trial period for the subscription, enhancing user acquisition.
        
        Args:
            trial_days (int): Number of trial days.
            
        Returns:
            bool: True if trial started successfully, False otherwise.
        """
        try:
            if trial_days <= 0:
                logging.error("Trial days must be positive")
                return False
            self.trial_end_date = self.data.payment_date + timedelta(days=trial_days)
            self.data.status = SubscriptionStatus.PENDING
            self.data.metadata["trial_start"] = datetime.utcnow().isoformat()
            self.data.metadata["trial_days"] = trial_days
            logging.info(f"Trial started for subscription {self.subscription_id} (ends: {self.trial_end_date})")
            return True
        except Exception as e:
            logging.error(f"Failed to start trial: {e}")
            return False

    @retry(Exception, tries=MAX_PAYMENT_RETRIES, delay=2, backoff=2)
    def process_payment(self, amount: Optional[float] = None) -> bool:
        """
        Process a payment with retry logic, simulating integration with a payment gateway.
        
        Args:
            amount (Optional[float]): Payment amount; defaults to plan price.
            
        Returns:
            bool: True if payment processed successfully, False otherwise.
        """
        try:
            amount = amount or PLAN_CYCLES[self.data.plan_type]["price"]
            if self.data.discount_code and "discount_applied" in self.data.metadata:
                discount = self.data.metadata["discount_applied"]["percentage"]
                amount *= (1 - discount / 100)
            
            # Simulate payment processing
            logging.info(f"Processing payment for subscription {self.subscription_id}: {amount:.2f} {DEFAULT_CURRENCY}")
            # Placeholder for actual payment gateway integration (e.g., Stripe, PayPal)
            
            self.data.payment_date = datetime.utcnow()
            self.next_payment_date = self.calculate_next_payment()
            self.data.status = SubscriptionStatus.ACTIVE
            self.data.metadata["last_payment"] = {
                "amount": amount,
                "currency": DEFAULT_CURRENCY,
                "timestamp": datetime.utcnow().isoformat()
            }
            logging.info(f"Payment processed for subscription {self.subscription_id}")
            return True
        except Exception as e:
            logging.error(f"Payment failed for subscription {self.subscription_id}: {e}")
            raise

    def cancel_subscription(self) -> bool:
        """
        Cancel the subscription, supporting user retention strategies.
        
        Returns:
            bool: True if cancellation successful, False otherwise.
        """
        try:
            if self.data.status == SubscriptionStatus.CANCELLED:
                logging.warning(f"Subscription {self.subscription_id} already cancelled")
                return False
            self.data.status = SubscriptionStatus.CANCELLED
            self.data.auto_pay = False
            self.data.metadata["cancelled_at"] = datetime.utcnow().isoformat()
            logging.info(f"Subscription {self.subscription_id} cancelled")
            return True
        except Exception as e:
            logging.error(f"Failed to cancel subscription {self.subscription_id}: {e}")
            return False

    def check_status(self) -> SubscriptionStatus:
        """
        Check and update subscription status based on payment and trial status.
        
        Returns:
            SubscriptionStatus: Current status of the subscription.
        """
        try:
            now = datetime.utcnow()
            if self.data.status == SubscriptionStatus.CANCELLED:
                return self.data.status
            if self.trial_end_date and now > self.trial_end_date:
                self.data.status = SubscriptionStatus.EXPIRED
                logging.warning(f"Subscription {self.subscription_id} trial expired")
            elif now > self.next_payment_date + timedelta(days=GRACE_PERIOD_DAYS):
                self.data.status = SubscriptionStatus.EXPIRED
                logging.warning(f"Subscription {self.subscription_id} expired (past grace period)")
            return self.data.status
        except Exception as e:
            logging.error(f"Status check failed for subscription {self.subscription_id}: {e}")
            return self.data.status

    def get_subscription_details(self) -> Dict[str, Any]:
        """
        Return detailed subscription information, supporting user transparency and analytics.
        
        Returns:
            Dict[str, Any]: Subscription details.
        """
        try:
            self.check_status()
            details = self.data.dict()
            details.update({
                "subscription_id": self.subscription_id,
                "next_payment_date": self.next_payment_date.strftime("%Y-%m-%d"),
                "trial_end_date": self.trial_end_date.strftime("%Y-%m-%d") if self.trial_end_date else None,
                "plan_price": PLAN_CYCLES[self.data.plan_type]["price"],
                "currency": DEFAULT_CURRENCY
            })
            logging.info(f"Retrieved details for subscription {self.subscription_id}")
            return details
        except Exception as e:
            logging.error(f"Failed to retrieve subscription details: {e}")
            return {}

def main() -> None:
    """Main function demonstrating subscription management capabilities."""
    try:
        # Create a sample subscription
        user_subscription = Subscription(
            user_id=1,
            plan_type="bi-weekly",
            payment_date=datetime.now(),
            auto_pay=True
        )
        
        # Apply a discount
        user_subscription.apply_discount("SUMMER25", 25.0)
        
        # Start a trial
        user_subscription.start_trial(14)
        
        # Process a payment
        user_subscription.process_payment()
        
        # Print subscription details
        print(user_subscription.get_subscription_details())
        
        # Simulate cancellation
        user_subscription.cancel_subscription()
        print(user_subscription.get_subscription_details())
    except Exception as e:
        logging.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()
