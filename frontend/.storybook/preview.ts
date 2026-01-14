import type { Preview } from '@storybook/vue3-vite'

// Import design tokens and Tailwind
import '../src/assets/main.css'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#F8FAFC' },
        { name: 'dark', value: '#0F172A' },
        { name: 'neutral', value: '#F4F4F5' },
      ],
    },
  },
};

export default preview;
