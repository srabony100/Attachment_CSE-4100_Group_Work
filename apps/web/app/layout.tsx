import "./globals.css";
import type { Metadata } from "next";
import { Playfair_Display, Space_Grotesk } from "next/font/google";
import Providers from "@/app/providers";

const spaceGrotesk = Space_Grotesk({
    subsets: ["latin"],
    variable: "--font-space-grotesk",
});

const playfair = Playfair_Display({
    subsets: ["latin"],
    variable: "--font-playfair",
});

export const metadata: Metadata = {
    title: "Semantic Programming Search",
    description: "Find programming answers with semantic vector search.",
};

export default function RootLayout({
    children,
}: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${spaceGrotesk.variable} ${playfair.variable} antialiased`}>
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
