import ReactMarkdown from 'react-markdown';

interface MarkdownTextProps {
    children: string;
    className?: string;
}

/** react-markdown never renders raw HTML, so owner-written messages cannot inject markup. */
export default function MarkdownText({ children, className }: MarkdownTextProps) {
    return (
        <div className={className}>
            <ReactMarkdown>{children}</ReactMarkdown>
        </div>
    );
}
