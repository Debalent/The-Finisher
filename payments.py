from fastapi import APIRouter

# Initialize FastAPI router
router = APIRouter()

# Define enhanced subscription plans
PLANS = {
    "free": {
        "features": [
            "5 lyric generations per month",
            "Non-commercial use only (attribution required)",
            "Basic customization (genre, mood, BPM, theme)"
        ],
        "pricing": {
            "monthly": 0
        }
    },
    "basic": {
        "features": [
            "50 lyric generations per month",
            "Commercial use for personal projects or small-scale monetization (e.g., videos with <10,000 views)",
            "All basic customization options",
            "Save up to 10 generated lyrics"
        ],
        "pricing": {
            "monthly": 30,
            "annually": 280  # ~$23.33/month, save ~$80/year vs monthly
        }
    },
    "pro": {
        "features": [
            "Unlimited lyric generations",
            "Full commercial use rights (no restrictions)",
            "Advanced customization (detailed prompts, rhyme schemes, meter control)",
            "Access to all genres and premium models",
            "Save unlimited generated lyrics",
            "Priority customer support",
            "Early access to new features (e.g., melody assistance, DAW integration)"
        ],
        "pricing": {
            "monthly": 50,
            "annually": 450,  # ~$37.5/month, save ~$100/year vs monthly
            "bi_annually": 800  # ~$33.33/month, save more over 2 years
        }
    }
}

# Endpoint to retrieve subscription plans
@router.get("/plans")
def get_plans():
    """
    Retrieve the available subscription plans with their features and pricing.
    
    Returns:
        dict: A dictionary containing the subscription plans.
    """
    return PLANS

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router, prefix="/api")
    uvicorn.run(app, host="0.0.0.0", port=8000)
