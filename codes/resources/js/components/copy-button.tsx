import { Button } from '@/components/ui/button';
import { useCopyToClipboard } from '@/hooks/use-copy-to-clipboard';
import { Check, Copy } from 'lucide-react';

interface CopyButtonProps {
    text: string;
    label?: string;
}

export default function CopyButton({ text, label = 'Copy' }: CopyButtonProps) {
    const { copied, copy } = useCopyToClipboard();

    return (
        <Button type="button" variant="outline" size="sm" onClick={() => void copy(text)}>
            {copied ? <Check key="done" className="ico-swap ico-draw size-4" /> : <Copy key="idle" className="size-4" />}
            {copied ? 'Copied' : label}
        </Button>
    );
}
