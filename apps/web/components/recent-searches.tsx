type RecentSearchesProps = {
    items: string[];
    onSelect: (query: string) => void;
    onClear: () => void;
};

export default function RecentSearches({ items, onSelect, onClear }: RecentSearchesProps) {
    if (items.length === 0) {
        
    }

    return (
        <section className="rounded-3xl border border-slate-300/40 bg-white/50 p-4 shadow-lg backdrop-blur dark:border-slate-700/50 dark:bg-slate-900/40">
            <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Recent searches</h3>
                <button
                    type="button"
                    onClick={onClear}
                    className="text-xs text-slate-500 transition hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-100"
                >
                    Clear
                </button>
            </div>
            <div className="flex flex-wrap gap-2">
                {items.map((item) => (
                    <button
                        key={item}
                        type="button"
                        onClick={() => onSelect(item)}
                        className="rounded-full border border-slate-300/70 bg-white/70 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-cyan-500/50 hover:bg-cyan-100/80 dark:border-slate-700/70 dark:bg-slate-900/60 dark:text-slate-200 dark:hover:border-cyan-300/50 dark:hover:bg-cyan-900/30"
                    >
                        {item}
                    </button>
                ))}
            </div>
        </section>
    );
}
