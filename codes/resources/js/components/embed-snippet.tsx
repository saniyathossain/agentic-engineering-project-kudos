import { Button } from '@/components/ui/button';
import { useCopyToClipboard } from '@/hooks/use-copy-to-clipboard';
import { Check, Copy } from 'lucide-react';

interface EmbedSnippetProps {
    publicId: string;
}

function buildEmbedSnippet(origin: string, publicId: string): string {
    return `<iframe src="${origin}/embed/${publicId}" width="100%" height="600" frameborder="0" style="border:0" loading="lazy" title="Testimonials"></iframe>`;
}

export default function EmbedSnippet({ publicId }: EmbedSnippetProps) {
    const { copied, copy } = useCopyToClipboard();
    const snippet = buildEmbedSnippet(window.location.origin, publicId);

    return (
        <div className="space-y-2">
            <pre className="bg-muted overflow-x-auto rounded-md border p-3 text-xs break-all whitespace-pre-wrap">
                <code>{snippet}</code>
            </pre>
            <Button type="button" variant="outline" size="sm" onClick={() => void copy(snippet)}>
                {copied ? <Check /> : <Copy />}
                {copied ? 'Copied' : 'Copy'}
            </Button>
        </div>
    );
}
