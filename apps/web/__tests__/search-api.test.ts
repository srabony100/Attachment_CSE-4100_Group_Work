import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchSemanticSearch } from "../lib/search-api";

describe("fetchSemanticSearch", () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it("returns normalized search payload for successful responses", async () => {
        vi.spyOn(global, "fetch").mockResolvedValue(
            new Response(
                JSON.stringify({
                    query: "how to sort list",
                    results: [
                        {
                            record_id: "js-1",
                            title: "How to sort a list in JavaScript",
                            answer_snippet: "Use array.sort((a, b) => a - b)",
                            tags: ["javascript"],
                            similarity_score: 0.92,
                        },
                    ],
                }),
                { status: 200, headers: { "Content-Type": "application/json" } },
            ),
        );

        const result = await fetchSemanticSearch("how to sort list", { topK: 1 });

        expect(result.query).toBe("how to sort list");
        expect(result.results).toHaveLength(1);
        expect(result.results[0]?.record_id).toBe("js-1");
    });

    it("maps auth errors to a user-friendly message", async () => {
        vi.spyOn(global, "fetch").mockResolvedValue(
            new Response(JSON.stringify({ detail: "Not authenticated" }), {
                status: 401,
                headers: { "Content-Type": "application/json" },
            }),
        );

        await expect(fetchSemanticSearch("python array")).rejects.toThrow(
            "Your session has expired or your account is blocked. Please login again.",
        );
    });

    it("shows connectivity message when backend is unreachable", async () => {
        vi.spyOn(global, "fetch").mockRejectedValue(new Error("network down"));

        await expect(fetchSemanticSearch("python array")).rejects.toThrow(
            "Could not reach the backend API. Make sure it is running on http://localhost:8000.",
        );
    });
});
