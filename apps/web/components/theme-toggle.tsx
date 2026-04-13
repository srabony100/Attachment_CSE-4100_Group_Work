"use client";

type Theme = "light" | "dark";

type ThemeToggleProps = {
    theme: Theme;
    onToggle: () => void;
};

export default function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
    const isDark = theme === "dark";

    return (
        <button
            type="button"
            onClick={onToggle}
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
            className="group inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-3 py-2 text-sm font-medium text-slate-800 shadow-lg backdrop-blur transition hover:bg-white/20 dark:border-white/20 dark:bg-slate-900/40 dark:text-slate-100 dark:hover:bg-slate-800/60"
        >
            <span
                aria-hidden
                className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/70 text-slate-900 transition group-hover:scale-105 dark:bg-slate-200 dark:text-slate-900"
            >
                {isDark ? "☀" : "☾"}
            </span>
            <span>{isDark ? "Light" : "Dark"}</span>
        </button>
    );
}
