import React from "react";
import LogoEmbed from "./LogoEmbed"; // Import the Canva logo component
import "./App.css"; // Import styles

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>The Finisher</h1>
        <p>Streamline your creative workflow with efficiency.</p>
        <LogoEmbed /> {/* Display the Canva logo */}
      </header>
    </div>
  );
}

export default App;
