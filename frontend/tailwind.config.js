/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Mastery level colors per FR-020
        mastery: {
          beginner: '#EF4444',    // Red (0-40%)
          learning: '#F59E0B',    // Yellow (41-70%)
          proficient: '#10B981',  // Green (71-90%)
          mastered: '#3B82F6',    // Blue (91-100%)
        },
      },
    },
  },
  plugins: [],
}
