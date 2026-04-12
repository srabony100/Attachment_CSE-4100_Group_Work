"use client";

import { ChangeEvent, useEffect, useState } from "react";

import {
    deleteAdminFile,
    listAdminFiles,
    previewFileChunks,
    reindexFiles,
    type FileChunkPreviewItem,
    type UploadedFileItem,
    uploadAdminFile,
} from "@/lib/admin-api";

export default function AdminFilesPage() {
    const [files, setFiles] = useState<UploadedFileItem[]>([]);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<FileChunkPreviewItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    async function loadFiles() {
        const payload = await listAdminFiles();
        setFiles(payload.files);
    }

    useEffect(() => {
        void loadFiles();
    }, []);

    async function handleUpload() {
        if (!selectedFile) {
            return;
        }
        setLoading(true);
        setError(null);
        setStatus(null);
        try {
            await uploadAdminFile(selectedFile);
            setStatus("File uploaded and indexed.");
            setSelectedFile(null);
            await loadFiles();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
            setLoading(false);
        }
    }

    async function handleDelete(fileId: number) {
        setLoading(true);
        setError(null);
        setStatus(null);
        try {
            await deleteAdminFile(fileId);
            setStatus("File deleted and index refreshed.");
            await loadFiles();
            setPreview([]);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Delete failed");
        } finally {
            setLoading(false);
        }
    }

    async function handlePreview(fileId: number) {
        setLoading(true);
        setError(null);
        try {
            const payload = await previewFileChunks(fileId);
            setPreview(payload.chunks);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Preview failed");
        } finally {
            setLoading(false);
        }
    }

    async function handleReindex() {
        setLoading(true);
        setError(null);
        setStatus(null);
        try {
            const payload = await reindexFiles();
            setStatus(`Reindex complete. ${payload.indexed_records} records indexed.`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Reindex failed");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="space-y-6">
            <h1 className="font-display text-4xl">File Management</h1>

            <section className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                <p className="text-sm text-slate-300">Upload supported formats: .txt, .md, .json, .pdf, .docx</p>
                <div className="mt-4 flex flex-wrap items-center gap-3">
                    <input
                        type="file"
                        onChange={(event: ChangeEvent<HTMLInputElement>) => {
                            const next = event.target.files?.[0] ?? null;
                            setSelectedFile(next);
                        }}
                        className="text-sm"
                    />
                    <button
                        type="button"
                        disabled={!selectedFile || loading}
                        onClick={() => void handleUpload()}
                        className="rounded-xl bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-60"
                    >
                        Upload and Index
                    </button>
                    <button
                        type="button"
                        disabled={loading}
                        onClick={() => void handleReindex()}
                        className="rounded-xl border border-white/20 px-4 py-2 text-sm hover:bg-white/10"
                    >
                        Trigger Reindex
                    </button>
                </div>
                {status ? <p className="mt-3 text-sm text-emerald-300">{status}</p> : null}
                {error ? <p className="mt-3 text-sm text-red-300">{error}</p> : null}
            </section>

            <section className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                <h2 className="font-display text-2xl">Uploaded Files</h2>
                <div className="mt-4 space-y-3">
                    {files.map((file) => (
                        <article key={file.id} className="rounded-xl border border-white/10 bg-black/20 p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                                <div>
                                    <p className="text-sm text-slate-200">{file.original_name}</p>
                                    <p className="text-xs text-slate-400">
                                        {file.chunk_count} chunks • {(file.size_bytes / 1024).toFixed(1)} KB
                                    </p>
                                </div>
                                <div className="flex gap-2 text-xs">
                                    <button
                                        type="button"
                                        onClick={() => void handlePreview(file.id)}
                                        className="rounded-lg border border-cyan-300/30 px-3 py-1.5 text-cyan-200 hover:bg-cyan-500/10"
                                    >
                                        Preview Chunks
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => void handleDelete(file.id)}
                                        className="rounded-lg border border-red-300/30 px-3 py-1.5 text-red-200 hover:bg-red-500/10"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </article>
                    ))}
                    {files.length === 0 ? <p className="text-sm text-slate-400">No uploaded files yet.</p> : null}
                </div>
            </section>

            <section className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                <h2 className="font-display text-2xl">Chunk Preview</h2>
                <div className="mt-4 space-y-3">
                    {preview.map((chunk) => (
                        <article key={chunk.id} className="rounded-xl border border-white/10 bg-black/20 p-4">
                            <p className="text-xs text-cyan-200">Chunk {chunk.chunk_index + 1}</p>
                            <p className="mt-2 text-sm text-slate-300">{chunk.preview_text}</p>
                        </article>
                    ))}
                    {preview.length === 0 ? <p className="text-sm text-slate-400">Select a file to preview its chunks.</p> : null}
                </div>
            </section>
        </div>
    );
}
