import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: "class",
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ["var(--font-space-grotesk)", "sans-serif"],
                display: ["var(--font-playfair)", "serif"],
            },
            colors: {
                ink: "#111827",
                tide: "#0f766e",
                mist: "#f8fafc",
                ember: "#c2410c",
            },
            boxShadow: {
                card: "0 10px 30px rgba(2, 132, 199, 0.12)",
            },
            keyframes: {
                drift: {
                    "0%, 100%": { transform: "translate3d(0, 0, 0)" },
                    "50%": { transform: "translate3d(0, -10px, 0)" },
                },
            },
            animation: {
                drift: "drift 8s ease-in-out infinite",
            },
        },
    },
    plugins: [],
};

export default config;
