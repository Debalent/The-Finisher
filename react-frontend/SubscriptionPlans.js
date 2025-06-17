import React, { useState, useEffect } from "react";

function SubscriptionPlans() {
    const [plans, setPlans] = useState([]);

    useEffect(() => {
        fetch("/api/subscriptions")
            .then((res) => res.json())
            .then((data) => setPlans(data))
            .catch((error) => console.error("❌ Error loading subscriptions:", error));
    }, []);

    return (
        <div className="p-6 bg-gray-900 text-white">
            <h2 className="text-xl font-bold">Choose a Subscription Plan</h2>
            <ul>
                {plans.map((plan, index) => (
                    <li key={index} className="mt-4">
                        <strong>{plan.name}</strong> - ${plan.price} ({plan.duration_days} days)
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default SubscriptionPlans;
