type EmptyStateProps = {
    hasSearched: boolean;
    quickSuggestions?: string[];
    onSuggestionSelect?: (value: string) => void;
};

export function EmptyState({ hasSearched, quickSuggestions = [], onSuggestionSelect }: EmptyStateProps) {
    return (
        <div className="rounded-3xl border border-slate-300/40 bg-white/50 p-8 text-center shadow-xl backdrop-blur dark:border-slate-700/60 dark:bg-slate-900/40">
            <h3 className="font-display text-2xl text-slate-900 dark:text-slate-100">
                {hasSearched ? "No close matches found" : "Start with a smart query"}
            </h3>
            <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-600 dark:text-slate-300">
                {hasSearched
                    ? "Try a broader phrase, remove a strict tag filter, or ask the same idea in different words."
                    : "Type a development question and press Enter. Tip: press / anywhere to focus the search field instantly."}
            </p>

            {hasSearched && quickSuggestions.length > 0 && onSuggestionSelect ? (
                <div className="mx-auto mt-5 max-w-3xl">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Try one of these
                    </p>
                    <div className="mt-3 flex flex-wrap justify-center gap-2">
                        {quickSuggestions.map((suggestion) => (
                            <button
                                key={suggestion}
                                type="button"
                                onClick={() => onSuggestionSelect(suggestion)}
                                className="rounded-full border border-slate-300/70 bg-white/70 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-cyan-500/50 hover:bg-cyan-100/80 dark:border-slate-700/70 dark:bg-slate-900/60 dark:text-slate-200 dark:hover:border-cyan-300/50 dark:hover:bg-cyan-900/30"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            ) : null}
        </div>
    );
}

export function LoadingState() {
    return (
        <div className="grid gap-4">
            {[0, 1, 2].map((item) => (
                <div
                    key={item}
                    className="animate-pulse rounded-3xl border border-slate-300/30 bg-white/60 p-6 shadow-lg backdrop-blur dark:border-slate-700/50 dark:bg-slate-900/50"
                >
                    <div className="h-4 w-1/3 rounded bg-slate-300/70 dark:bg-slate-700/70" />
                    <div className="mt-4 h-5 w-2/3 rounded bg-slate-300/70 dark:bg-slate-700/70" />
                    <div className="mt-3 h-4 w-full rounded bg-slate-200/80 dark:bg-slate-800/80" />
                    <div className="mt-2 h-4 w-5/6 rounded bg-slate-200/80 dark:bg-slate-800/80" />
                </div>
            ))}
        </div>
    );
}
