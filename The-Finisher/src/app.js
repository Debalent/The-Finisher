import React, { useState, useEffect } from 'react';
import axios from 'axios';
import LogoEmbed from './LogoEmbed'; // Import the Canva logo component
import './App.css'; // Retain for custom styles (e.g., LogoEmbed)

function App() {
  const [plans, setPlans] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch subscription plans from the backend
    axios.get('http://localhost:8000/api/plans')
      .then(response => setPlans(response.data))
      .catch(err => setError('Failed to load plans. Please try again later.'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">The Finisher</h1>
        <p className="text-lg text-gray-700 mb-6">Streamline your creative workflow with efficiency.</p>
        <LogoEmbed />
      </header>
      <section className="w-full max-w-5xl">
        {error && <p className="text-red-500 text-center mb-4">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(plans).map(([planName, plan]) => (
            <div key={planName} className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold capitalize mb-4">{planName}</h2>
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
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                disabled={planName === 'free'}
              >
                {planName === 'free' ? 'Current Plan' : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;
