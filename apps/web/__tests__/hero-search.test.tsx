// @vitest-environment jsdom
import React from "react";
import { createRef } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import HeroSearch from "../components/hero-search";

function renderHeroSearch(overrides?: Partial<React.ComponentProps<typeof HeroSearch>>) {
    const props: React.ComponentProps<typeof HeroSearch> = {
        query: "",
        loading: false,
        error: null,
        suggestions: ["How to sort a list in JavaScript", "How to declare array in Python"],
        activeSuggestion: -1,
        isSuggesting: false,
        suggestionMessage: null,
        inputRef: createRef<HTMLInputElement>(),
        onQueryChange: vi.fn(),
        onSubmit: vi.fn(),
        onSuggestionSelect: vi.fn(),
        onActiveSuggestionChange: vi.fn(),
        ...overrides,
    };

    render(<HeroSearch {...props} />);
    return props;
}

describe("HeroSearch", () => {
    it("disables submit button for short query", () => {
        renderHeroSearch({ query: "ab" });

        const button = screen.getByRole("button", { name: "Search" });
        expect(button).toBeDisabled();
    });

    it("submits the form when query is valid", () => {
        const props = renderHeroSearch({ query: "how to sort a list" });

        fireEvent.click(screen.getByRole("button", { name: "Search" }));

        expect(props.onSubmit).toHaveBeenCalledTimes(1);
    });

    it("selects highlighted suggestion on Enter", () => {
        const props = renderHeroSearch({
            query: "how",
            activeSuggestion: 1,
        });

        fireEvent.keyDown(screen.getByRole("textbox", { name: /search programming questions/i }), {
            key: "Enter",
            code: "Enter",
        });

        expect(props.onSuggestionSelect).toHaveBeenCalledWith("How to declare array in Python");
    });
});
