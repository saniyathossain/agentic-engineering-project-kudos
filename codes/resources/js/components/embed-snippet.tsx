import CopyButton from '@/components/copy-button';

interface EmbedSnippetProps {
    publicId: string;
}

function buildEmbedSnippet(origin: string, publicId: string): string {
    return `<iframe src="${origin}/embed/${publicId}" width="100%" height="600" frameborder="0" style="border:0" loading="lazy" title="Testimonials"></iframe>`;
}

export default function EmbedSnippet({ publicId }: EmbedSnippetProps) {
    const snippet = buildEmbedSnippet(window.location.origin, publicId);

    return (
        <div className="space-y-2">
            <pre className="bg-muted/70 overflow-x-auto rounded-xl border p-3 font-mono text-xs leading-relaxed break-all whitespace-pre-wrap">
                <code>{snippet}</code>
            </pre>
            <CopyButton text={snippet} />
        </div>
    );
}
