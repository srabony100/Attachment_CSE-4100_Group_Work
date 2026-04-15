"use client";

import React from "react";
import { type FormEvent, type KeyboardEvent, type RefObject } from "react";

type HeroSearchProps = {
    query: string;
    loading: boolean;
    error: string | null;
    suggestions: string[];
    activeSuggestion: number;
    isSuggesting: boolean;
    suggestionMessage: string | null;
    inputRef: RefObject<HTMLInputElement>;
    onQueryChange: (next: string) => void;
    onSubmit: () => void;
    onSuggestionSelect: (value: string) => void;
    onActiveSuggestionChange: (index: number) => void;
};

export default function HeroSearch({
    query,
    loading,
    error,
    suggestions,
    activeSuggestion,
    isSuggesting,
    suggestionMessage,
    inputRef,
    onQueryChange,
    onSubmit,
    onSuggestionSelect,
    onActiveSuggestionChange,
}: HeroSearchProps) {
    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        onSubmit();
    }

    function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
        if (suggestions.length === 0) {
            return;
        }

        if (event.key === "ArrowDown") {
            event.preventDefault();
            onActiveSuggestionChange((activeSuggestion + 1) % suggestions.length);
            return;
        }

        if (event.key === "ArrowUp") {
            event.preventDefault();
            onActiveSuggestionChange((activeSuggestion - 1 + suggestions.length) % suggestions.length);
            return;
        }

        if (event.key === "Enter" && activeSuggestion >= 0 && suggestions[activeSuggestion]) {
            event.preventDefault();
            onSuggestionSelect(suggestions[activeSuggestion]);
            return;
        }

        if (event.key === "Escape") {
            onActiveSuggestionChange(-1);
        }
    }

    return (
        <section className="relative rounded-[2rem] border border-white/35 bg-white/45 p-6 shadow-2xl backdrop-blur-xl dark:border-white/10 dark:bg-slate-900/45 md:p-10">
            <div className="pointer-events-none absolute -top-28 left-1/2 h-56 w-56 -translate-x-1/2 rounded-full bg-cyan-400/25 blur-3xl dark:bg-cyan-400/15" />

            <div className="relative z-10 text-center">
                <p className="mx-auto inline-flex items-center rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-900 dark:text-cyan-200">
                    Semantic Engine
                </p>
                <h1 className="font-display mt-4 text-4xl leading-tight text-slate-900 dark:text-white md:text-6xl">
                    Find the right programming answer,
                    <span className="block text-cyan-700 dark:text-cyan-300">even if wording is different.</span>
                </h1>
                <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-slate-600 dark:text-slate-300 md:text-base">
                    Search across semantically similar coding questions using fresh embeddings and vector similarity.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="relative z-10 mx-auto mt-8 max-w-4xl">
                <label htmlFor="hero-search" className="sr-only">
                    Search programming questions
                </label>
                <div className="flex flex-col gap-3 rounded-2xl border border-slate-300/60 bg-white/80 p-3 shadow-xl dark:border-slate-700/60 dark:bg-slate-900/70 md:flex-row md:items-center">
                    <input
                        id="hero-search"
                        ref={inputRef}
                        value={query}
                        onChange={(event) => {
                            onQueryChange(event.target.value);
                            onActiveSuggestionChange(-1);
                        }}
                        onKeyDown={onKeyDown}
                        placeholder="Try: Why does React useEffect run twice in dev mode?"
                        className="w-full rounded-xl border border-transparent bg-transparent px-3 py-3 text-base text-slate-900 outline-none placeholder:text-slate-500 focus:border-cyan-500/40 dark:text-slate-100 dark:placeholder:text-slate-400"
                        aria-autocomplete="list"
                        aria-controls="search-suggestions"
                        aria-activedescendant={
                            activeSuggestion >= 0 ? `suggestion-${activeSuggestion}` : undefined
                        }
                    />
                    <button
                        type="submit"
                        disabled={loading || query.trim().length < 3}
                        className="rounded-xl bg-gradient-to-r from-cyan-700 to-teal-600 px-6 py-3 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                        {loading ? "Searching..." : "Search"}
                    </button>
                </div>

                <div id="search-suggestions" className="mt-4 flex flex-wrap justify-center gap-2" role="listbox">
                    {suggestions.map((suggestion, index) => (
                        <button
                            id={`suggestion-${index}`}
                            key={suggestion}
                            type="button"
                            role="option"
                            aria-selected={index === activeSuggestion}
                            onClick={() => onSuggestionSelect(suggestion)}
                            onMouseEnter={() => onActiveSuggestionChange(index)}
                            className={`rounded-full border px-3 py-1.5 text-xs font-medium transition md:text-sm ${index === activeSuggestion
                                ? "border-cyan-500/60 bg-cyan-500/20 text-cyan-900 dark:text-cyan-100"
                                : "border-slate-300/70 bg-white/70 text-slate-700 hover:border-cyan-400/50 hover:bg-cyan-100/70 dark:border-slate-700/70 dark:bg-slate-900/60 dark:text-slate-200"
                                }`}
                        >
                            {suggestion}
                        </button>
                    ))}
                </div>

                {isSuggesting ? (
                    <p className="mt-3 text-center text-xs text-cyan-800 dark:text-cyan-200">
                        Refreshing live suggestions...
                    </p>
                ) : null}

                {suggestionMessage ? (
                    <p className="mt-3 text-center text-xs text-amber-700 dark:text-amber-300">{suggestionMessage}</p>
                ) : null}

                <p className="mt-3 text-center text-xs text-slate-500 dark:text-slate-400">
                    Keyboard: press <kbd className="rounded border px-1.5 py-0.5">/</kbd> to focus, arrows to browse suggestions, Enter to search.
                </p>
            </form>

            {error ? <p className="mt-4 text-center text-sm text-orange-700 dark:text-orange-300">{error}</p> : null}
        </section>
    );
}
