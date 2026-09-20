/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Capco-inspired professional color palette
        capco: {
          navy: '#002B5B',      // Primary navy blue
          blue: '#0066CC',      // Capco blue
          lightBlue: '#4A90E2', // Light accent blue
          gray: {
            50: '#F8F9FA',
            100: '#F1F3F5',
            200: '#E9ECEF',
            300: '#DEE2E6',
            400: '#CED4DA',
            500: '#ADB5BD',
            600: '#6C757D',
            700: '#495057',
            800: '#343A40',
            900: '#212529',
          },
          green: '#28A745',     // Success
          yellow: '#FFC107',    // Warning
          red: '#DC3545',       // Danger/Alert
          orange: '#FD7E14',    // Priority
        },
        primary: {
          50: '#E6F0FF',
          100: '#CCE1FF',
          200: '#99C3FF',
          300: '#66A5FF',
          400: '#3387FF',
          500: '#0066CC',      // Main primary
          600: '#0052A3',
          700: '#003D7A',
          800: '#002952',
          900: '#001429',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Helvetica Neue', 'Arial', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'capco': '0 2px 8px rgba(0, 43, 91, 0.1)',
        'capco-lg': '0 4px 16px rgba(0, 43, 91, 0.15)',
        'capco-xl': '0 8px 24px rgba(0, 43, 91, 0.2)',
      },
      borderRadius: {
        'capco': '8px',
      },
    },
  },
  plugins: [],
}
