import type { Config } from "tailwindcss"
import tailwindcssAnimate from "tailwindcss-animate"
import typography from "@tailwindcss/typography"

/**
 * Quantum Studio Tailwind Config v3.1
 * 
 * Visual System: "Zinc & Flow"
 * - Canvas: bg-zinc-50
 * - Islands: bg-white + shadow-sm + border-zinc-100
 * - Primary: 纯黑 #18181b (zinc-900)
 */
const config = {
    darkMode: "class",
    content: [
        './pages/**/*.{ts,tsx}',
        './components/**/*.{ts,tsx}',
        './app/**/*.{ts,tsx}',
        './src/**/*.{ts,tsx}',
        './src/features/**/*.{js,ts,jsx,tsx}',
    ],
    prefix: "",
    theme: {
        container: {
            center: true,
            padding: "2rem",
            screens: {
                "2xl": "1400px",
            },
        },
        extend: {
            colors: {
                // === v3.1 Quantum Studio Design Tokens ===

                // Canvas Layer (全局背景)
                canvas: "#FAFAFA",  // zinc-50 equivalent

                // Island Layer (悬浮岛屿)
                island: "#FFFFFF",

                // Semantic Colors
                primary: {
                    DEFAULT: "#18181B",  // zinc-900 - 纯黑
                    foreground: "#FAFAFA",
                },
                secondary: {
                    DEFAULT: "#F4F4F5",  // zinc-100
                    foreground: "#18181B",
                },
                muted: {
                    DEFAULT: "#F4F4F5",
                    foreground: "#71717A",  // zinc-500
                },
                accent: {
                    DEFAULT: "#F4F4F5",
                    foreground: "#18181B",
                },
                destructive: {
                    DEFAULT: "#EF4444",
                    foreground: "#FAFAFA",
                },

                // Text Colors
                ink: {
                    primary: "#18181B",   // zinc-900
                    secondary: "#3F3F46", // zinc-700
                    muted: "#71717A",     // zinc-500
                    faint: "#A1A1AA",     // zinc-400
                },

                // Border Colors
                border: "#E4E4E7",        // zinc-200
                hairline: "#F4F4F5",      // zinc-100

                // Legacy compatibility
                background: "#FAFAFA",
                foreground: "#18181B",
                card: {
                    DEFAULT: "#FFFFFF",
                    foreground: "#18181B",
                },
                popover: {
                    DEFAULT: "#FFFFFF",
                    foreground: "#18181B",
                },
                input: "#E4E4E7",
                ring: "#18181B",
            },

            // === v3.1 Border Radius (12px base) ===
            borderRadius: {
                DEFAULT: "0.75rem",      // 12px - 标准
                lg: "1rem",              // 16px - 大卡片
                md: "0.75rem",           // 12px
                sm: "0.5rem",            // 8px
                xl: "1rem",              // 16px
                "2xl": "1.25rem",        // 20px
            },

            // === v3.1 Font Family ===
            fontFamily: {
                sans: ["var(--font-geist-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
                serif: ["var(--font-newsreader)", "ui-serif", "Georgia", "serif"],
                mono: ["var(--font-geist-mono)", "Consolas", "Monaco", "monospace"],
            },

            // === v3.1 Box Shadow (Island Effect) ===
            boxShadow: {
                'island': '0 1px 3px 0 rgb(0 0 0 / 0.04), 0 1px 2px -1px rgb(0 0 0 / 0.04)',
                'island-lg': '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
                'float': '0 10px 25px -5px rgb(0 0 0 / 0.08)',
            },

            // Animations
            keyframes: {
                "accordion-down": {
                    from: { height: "0" },
                    to: { height: "var(--radix-accordion-content-height)" },
                },
                "accordion-up": {
                    from: { height: "var(--radix-accordion-content-height)" },
                    to: { height: "0" },
                },
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
            },
        },
    },
    plugins: [tailwindcssAnimate, typography],
} satisfies Config

export default config
