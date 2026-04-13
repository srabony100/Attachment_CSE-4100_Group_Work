import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
    test: {
        environment: "jsdom",
        globals: true,
        setupFiles: ["./setupTests.ts"],
        include: ["__tests__/**/*.test.{ts,tsx}"],
    },
    esbuild: {
        jsx: "automatic",
        jsxImportSource: "react",
    },
    resolve: {
        alias: {
            "@": path.resolve(__dirname),
        },
    },
});
