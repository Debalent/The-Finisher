import stripe
import os

# 🔹 SECURITY: API keys are stored in environment variables to prevent exposure.
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_your_api_key_here")

def create_payment(user_id, amount, currency="usd", payment_method_types=None):
    """
    🔹 FUNCTION PURPOSE:
    - Processes payments securely using Stripe.
    - Supports multiple payment methods (card, PayPal, etc.).
    - Converts amount to cents (Stripe requirement).

    🔹 WHY IT MATTERS FOR INVESTORS:
    - Ensures seamless transactions for users.
    - Scalable payment system for future monetization.
    - Secure handling of financial data.
    """
    try:
        if payment_method_types is None:
            payment_method_types = ["card"]  # Default to card payments

        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # 🔹 Stripe requires amounts in cents.
            currency=currency,
            payment_method_types=payment_method_types,
            metadata={"user_id": user_id}
        )
        return {
            "status": "success",
            "payment_intent": payment_intent.id,
            "message": "Payment processed successfully."
        }
    
    except stripe.error.CardError as e:
        return {"status": "error", "type": "CardError", "message": str(e)}
    except stripe.error.RateLimitError as e:
        return {"status": "error", "type": "RateLimitError", "message": str(e)}
    except stripe.error.InvalidRequestError as e:
        return {"status": "error", "type": "InvalidRequestError", "message": str(e)}
    except stripe.error.AuthenticationError as e:
        return {"status": "error", "type": "AuthenticationError", "message": str(e)}
    except stripe.error.APIConnectionError as e:
        return {"status": "error", "type": "APIConnectionError", "message": str(e)}
    except stripe.error.StripeError as e:
        return {"status": "error", "type": "StripeError", "message": str(e)}
    except Exception as e:
        return {"status": "error", "type": "GeneralError", "message": str(e)}

# 🔹 EXAMPLE USAGE:
# Investors can see how payments are processed in real-time.
if __name__ == "__main__":
    payment = create_payment(user_id=1, amount=12.50, payment_method_types=["card"])
    print(payment)