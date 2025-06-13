import React from "react";

const LogoEmbed = () => {
  return (
    <div className="relative w-full h-0 pt-[100%] shadow-lg mt-6 mb-4 overflow-hidden rounded-lg">
      <iframe
        loading="lazy"
        className="absolute w-full h-full top-0 left-0 border-none"
        src="https://www.canva.com/design/DAGqGc_0wvY/nNd5SCGFSsdPiJ6_sbIwBA/watch?embed"
        allowFullScreen
      ></iframe>
    </div>
  );
};

export default LogoEmbed;
