// @vitest-environment jsdom
import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ResultCard from "../components/result-card";

const item = {
    record_id: "py-1",
    title: "How to declare an array in Python",
    answer_snippet: "Use a list like numbers = [1, 2, 3]",
    tags: ["python", "arrays"],
    similarity_score: 0.94,
};

describe("ResultCard", () => {
    it("renders core content and relevance", () => {
        render(<ResultCard item={item} index={0} query="declare array python" />);

        expect(screen.getByText("#py-1")).toBeInTheDocument();
        expect(screen.getByText(/94.0% match/)).toBeInTheDocument();
        expect(screen.getByText("python")).toBeInTheDocument();
    });

    it("expands to show full details", () => {
        render(<ResultCard item={item} index={0} query="declare array python" />);

        fireEvent.click(screen.getByRole("button", { name: "Expand details" }));

        expect(screen.getByText("Full details")).toBeInTheDocument();
        expect(screen.getByText(/Relevance score: 0.9400/)).toBeInTheDocument();
    });

    it("copies question title to clipboard", async () => {
        const writeText = vi.fn().mockResolvedValue(undefined);
        vi.stubGlobal("navigator", {
            clipboard: { writeText },
        });

        render(<ResultCard item={item} index={0} query="declare array python" />);
        fireEvent.click(screen.getByRole("button", { name: "Copy question" }));

        await waitFor(() => {
            expect(writeText).toHaveBeenCalledWith("How to declare an array in Python");
        });
    });
});
