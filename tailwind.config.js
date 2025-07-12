import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss()],
})

// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        electric: '#00FFFF',
        deepPurple: '#6B21A8',
        vibrantPink: '#FF007A',
      },
      fontFamily: {
        pop: ['Poppins', 'sans-serif'],
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
    },
  },
  plugins: [],
}
