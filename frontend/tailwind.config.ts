import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        priority: {
          critical: "#d62728",
          high: "#ff7f0e",
          medium: "#e3b505",
          low: "#2ca02c",
        },
      },
    },
  },
  plugins: [],
};

export default config;
