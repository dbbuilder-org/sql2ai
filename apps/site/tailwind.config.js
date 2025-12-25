const { createGlobPatternsForDependencies } = require('@nx/react/tailwind');
const { join } = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    join(__dirname, 'src/**/*.{js,ts,jsx,tsx,mdx}'),
    ...createGlobPatternsForDependencies(__dirname),
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Background layers
        bg: {
          base: '#09090f',
          surface: '#111118',
          elevated: '#18181f',
          overlay: '#1f1f27',
        },
        // Border colors
        border: {
          subtle: '#27272f',
          DEFAULT: '#3f3f47',
          emphasis: '#52525b',
        },
        // Text colors
        text: {
          primary: '#fafafa',
          secondary: '#a1a1aa',
          muted: '#71717a',
          disabled: '#52525b',
        },
        // Primary action color
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
          muted: '#1d4ed8',
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Semantic colors
        success: {
          DEFAULT: '#22c55e',
          muted: '#166534',
        },
        warning: {
          DEFAULT: '#eab308',
          muted: '#854d0e',
        },
        error: {
          DEFAULT: '#ef4444',
          muted: '#991b1b',
        },
        // Platform colors
        postgresql: '#336791',
        sqlserver: '#cc2927',
        // Diff colors
        diff: {
          add: {
            bg: 'rgba(34, 197, 94, 0.12)',
            border: 'rgba(34, 197, 94, 0.3)',
            text: '#22c55e',
          },
          remove: {
            bg: 'rgba(239, 68, 68, 0.12)',
            border: 'rgba(239, 68, 68, 0.3)',
            text: '#ef4444',
          },
          change: {
            bg: 'rgba(234, 179, 8, 0.12)',
            border: 'rgba(234, 179, 8, 0.3)',
            text: '#eab308',
          },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        h1: ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '600' }],
        h2: ['2.25rem', { lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '600' }],
        h3: ['1.75rem', { lineHeight: '1.3', letterSpacing: '-0.01em', fontWeight: '600' }],
        h4: ['1.375rem', { lineHeight: '1.4', fontWeight: '500' }],
        h5: ['1.125rem', { lineHeight: '1.4', fontWeight: '500' }],
        body: ['1rem', { lineHeight: '1.6' }],
        small: ['0.875rem', { lineHeight: '1.5' }],
        xs: ['0.75rem', { lineHeight: '1.5' }],
        code: ['0.875rem', { lineHeight: '1.5' }],
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'grid-pattern': `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%233f3f47' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      },
    },
  },
  plugins: [],
};
