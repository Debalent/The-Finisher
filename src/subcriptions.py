from datetime import datetime, timedelta

class Subscription:
    """Handles user subscription plans and billing cycles."""
    
    def __init__(self, user_id, plan_type, payment_date, auto_pay=True):
        self.user_id = user_id
        self.plan_type = plan_type.lower()
        self.payment_date = payment_date
        self.auto_pay = auto_pay
        self.next_payment_date = self.calculate_next_payment()

    def calculate_next_payment(self):
        """Determines next payment date based on plan type."""
        plan_cycles = {
            "monthly": timedelta(days=30),
            "bi-weekly": timedelta(days=14),
            "yearly": timedelta(days=365)
        }
        
        if self.plan_type in plan_cycles:
            return self.payment_date + plan_cycles[self.plan_type]
        else:
            raise ValueError("Invalid subscription plan")

    def get_subscription_details(self):
        """Returns subscription details in a structured format."""
        return {
            "user_id": self.user_id,
            "plan": self.plan_type.capitalize(),
            "payment_date": self.payment_date.strftime("%Y-%m-%d"),
            "next_payment_date": self.next_payment_date.strftime("%Y-%m-%d"),
            "auto_pay": self.auto_pay
        }

# Example Usage
if __name__ == "__main__":
    user_subscription = Subscription(user_id=1, plan_type="bi-weekly", payment_date=datetime.now())
    print(user_subscription.get_subscription_details())
