import stripe

# Stripe API Key (Use test keys for development)
stripe.api_key = "sk_test_your_api_key_here"

def create_payment(user_id, amount, currency="usd", payment_method="card"):
    """Process payment using Stripe."""
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency=currency,
            payment_method_types=[payment_method],
            metadata={"user_id": user_id}
        )
        return {"status": "success", "payment_intent": payment_intent.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Example Usage
if __name__ == "__main__":
    payment = create_payment(user_id=1, amount=12.50)
    print(payment)
