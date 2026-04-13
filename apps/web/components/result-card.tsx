"use client";

import React from "react";
import { useMemo, useState } from "react";

export type SearchResult = {
    record_id: string;
    title: string;
    answer_snippet: string;
    tags: string[];
    similarity_score?: number;
};

type ResultCardProps = {
    item: SearchResult;
    index: number;
    query?: string;
};

function escapeRegExp(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function getQueryTerms(query: string): string[] {
    return Array.from(
        new Set(
            query
                .toLowerCase()
                .split(/\s+/)
                .map((term) => term.trim())
                .filter((term) => term.length >= 3),
        ),
    ).slice(0, 8);
}

function highlightText(text: string, terms: string[]): Array<{ text: string; highlight: boolean }> {
    if (terms.length === 0) {
        return [{ text, highlight: false }];
    }

    const pattern = new RegExp(`(${terms.map(escapeRegExp).join("|")})`, "ig");
    const parts = text.split(pattern);
    return parts
        .filter((part) => part.length > 0)
        .map((part) => ({ text: part, highlight: terms.includes(part.toLowerCase()) }));
}

export default function ResultCard({ item, index, query = "" }: ResultCardProps) {
    const [expanded, setExpanded] = useState(false);
    const [copied, setCopied] = useState(false);

    const terms = useMemo(() => getQueryTerms(query), [query]);
    const highlightedTitle = useMemo(() => highlightText(item.title, terms), [item.title, terms]);
    const highlightedSnippet = useMemo(() => highlightText(item.answer_snippet, terms), [item.answer_snippet, terms]);

    async function handleCopyQuestion() {
        try {
            await navigator.clipboard.writeText(item.title);
            setCopied(true);
            window.setTimeout(() => setCopied(false), 1400);
        } catch {
            setCopied(false);
        }
    }

    return (
        <article
            className="group relative overflow-hidden rounded-3xl border border-slate-300/40 bg-white/60 p-6 shadow-xl backdrop-blur transition duration-500 hover:-translate-y-0.5 hover:shadow-2xl dark:border-slate-700/50 dark:bg-slate-900/50"
            style={{ animationDelay: `${index * 55}ms` }}
        >
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-cyan-300/0 via-cyan-400/10 to-orange-300/0 opacity-0 transition group-hover:opacity-100" />

            <div className="relative z-10 mb-3 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <span>#{item.record_id}</span>
                {typeof item.similarity_score === "number" ? (
                    <span className="rounded-full bg-cyan-500/10 px-3 py-1 font-semibold text-cyan-700 dark:text-cyan-300">
                        {(item.similarity_score * 100).toFixed(1)}% match
                    </span>
                ) : null}
            </div>

            <h2 className="relative z-10 text-xl font-semibold leading-snug text-slate-900 dark:text-slate-100">
                {highlightedTitle.map((part, partIndex) =>
                    part.highlight ? (
                        <mark
                            key={`${part.text}-${partIndex}`}
                            className="rounded bg-cyan-200/70 px-1 text-slate-900 dark:bg-cyan-500/40 dark:text-white"
                        >
                            {part.text}
                        </mark>
                    ) : (
                        <span key={`${part.text}-${partIndex}`}>{part.text}</span>
                    ),
                )}
            </h2>

            <p className={`relative z-10 mt-3 text-sm leading-6 text-slate-700 dark:text-slate-300 ${expanded ? "" : "line-clamp-4"}`}>
                {highlightedSnippet.map((part, partIndex) =>
                    part.highlight ? (
                        <mark
                            key={`${part.text}-${partIndex}`}
                            className="rounded bg-cyan-200/70 px-1 text-slate-900 dark:bg-cyan-500/40 dark:text-white"
                        >
                            {part.text}
                        </mark>
                    ) : (
                        <span key={`${part.text}-${partIndex}`}>{part.text}</span>
                    ),
                )}
            </p>

            <div className="relative z-10 mt-4 flex flex-wrap gap-2">
                {item.tags.map((tag) => (
                    <span
                        key={tag}
                        className="rounded-full border border-cyan-400/35 bg-cyan-50/70 px-2.5 py-1 text-xs font-medium text-cyan-900 dark:border-cyan-300/30 dark:bg-cyan-900/30 dark:text-cyan-100"
                    >
                        {tag}
                    </span>
                ))}
            </div>

            <div className="relative z-10 mt-5 flex flex-wrap gap-2">
                <button
                    type="button"
                    onClick={() => setExpanded((current) => !current)}
                    className="rounded-lg border border-slate-300/80 bg-white/70 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-cyan-500/60 hover:bg-cyan-100/80 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-200 dark:hover:border-cyan-300/60 dark:hover:bg-cyan-900/30"
                >
                    {expanded ? "Collapse details" : "Expand details"}
                </button>
                <button
                    type="button"
                    onClick={() => void handleCopyQuestion()}
                    className="rounded-lg border border-slate-300/80 bg-white/70 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-cyan-500/60 hover:bg-cyan-100/80 dark:border-slate-700 dark:bg-slate-900/70 dark:text-slate-200 dark:hover:border-cyan-300/60 dark:hover:bg-cyan-900/30"
                >
                    {copied ? "Copied" : "Copy question"}
                </button>
            </div>

            {expanded ? (
                <div className="relative z-10 mt-4 rounded-2xl border border-slate-300/70 bg-white/75 p-4 text-sm text-slate-700 dark:border-slate-700/80 dark:bg-slate-900/70 dark:text-slate-300">
                    <p className="font-medium text-slate-900 dark:text-slate-100">Full details</p>
                    <p className="mt-2 leading-6">{item.answer_snippet}</p>
                    {typeof item.similarity_score === "number" ? (
                        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                            Relevance score: {item.similarity_score.toFixed(4)}
                        </p>
                    ) : null}
                </div>
            ) : null}
        </article>
    );
}
