import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SubscriptionPlans() {
  const [plans, setPlans] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setIsLoading(true);
    axios.get('http://localhost:8000/api/plans')
      .then(response => {
        setPlans(response.data);
        setIsLoading(false);
      })
      .catch(error => {
        setError('Failed to load subscription plans. Please try again later.');
        setIsLoading(false);
        console.error('❌ Error loading subscriptions:', error);
      });
  }, []);

  const handleChoosePlan = (planName) => {
    // Stub for subscription logic (e.g., integrate with payments.py or Stripe)
    alert(`Selected plan: ${planName}`);
    // Future: Call API to initiate subscription (e.g., POST /api/subscribe)
  };

  return (
    <div className="p-6 bg-gray-100">
      <h2 className="text-2xl font-bold text-center text-blue-600 mb-8">Choose a Subscription Plan</h2>
      {isLoading && (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-600 mx-auto"></div>
          <p className="text-gray-700 mt-2">Loading plans...</p>
        </div>
      )}
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6" role="alert">
          <p>{error}</p>
        </div>
      )}
      {!isLoading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {Object.entries(plans).map(([planName, plan]) => (
            <div key={planName} className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <h3 className="text-xl font-semibold capitalize text-blue-600 mb-4">{planName}</h3>
              <ul className="mb-6">
                {plan.features.map((feature, index) => (
                  <li key={index} className="text-gray-700 mb-2">• {feature}</li>
                ))}
              </ul>
              <div className="mb-4">
                {Object.entries(plan.pricing).map(([cycle, price]) => (
                  <p key={cycle} className="text-gray-600">
                    {cycle.charAt(0).toUpperCase() + cycle.slice(1)}: ${price}
                  </p>
                ))}
              </div>
              <button
                onClick={() => handleChoosePlan(planName)}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                disabled={planName === 'free'}
              >
                {planName === 'free' ? 'Current Plan' : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SubscriptionPlans;
