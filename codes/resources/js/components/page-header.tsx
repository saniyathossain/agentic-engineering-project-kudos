import { type ReactNode } from 'react';

interface PageHeaderProps {
    title: string;
    description?: string;
    actions?: ReactNode;
}

export default function PageHeader({ title, description, actions }: PageHeaderProps) {
    return (
        <header className="rise flex flex-wrap items-end justify-between gap-4">
            <div className="min-w-0 space-y-1">
                <h1 className="font-display text-3xl leading-tight font-medium sm:text-4xl">{title}</h1>
                {description && <p className="text-muted-foreground max-w-prose text-[0.95rem]">{description}</p>}
            </div>
            {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
        </header>
    );
}
