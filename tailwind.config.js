/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        electric: '#00FFFF',
        deepPurple: '#6B21A8',
        vibrantPink: '#FF007A',
        midnight: '#1B1C2E',
      },
      fontFamily: {
        pop: ['Poppins', 'sans-serif'],
        techno: ['Orbitron', 'sans-serif'],
      },
      animation: {
        pulseFast: 'pulse 1s ease-in-out infinite',
        slideIn: 'slideIn 0.5s ease-out forwards',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateY(20px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
      },
      boxShadow: {
        glow: '0 0 10px #00FFFF',
      },
    },
  },
  plugins: [],
}
