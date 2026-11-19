import { Button } from '@/components/ui/button';
import { useClipboard } from '@/hooks/use-clipboard';
import { Check, Copy } from 'lucide-react';

interface CopyButtonProps {
    text: string;
    label?: string;
}

export default function CopyButton({ text, label = 'Copy' }: CopyButtonProps) {
    const { copied, copy } = useClipboard();

    return (
        <Button type="button" variant="outline" size="sm" onClick={() => void copy(text)}>
            {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
            {copied ? 'Copied' : label}
        </Button>
    );
}
