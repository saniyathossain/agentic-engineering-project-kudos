import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { type LucideIcon } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

const chipVariants = cva(
    'inline-flex shrink-0 items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs leading-none font-medium whitespace-nowrap transition-[background-color,color,border-color,box-shadow,transform] duration-200 ease-(--ease-liquid) focus-visible:outline-hidden focus-visible:ring-[3px] focus-visible:ring-ring/35 [&_svg]:size-3.5 [&_svg]:shrink-0',
    {
        variants: {
            tone: {
                neutral: 'border-transparent bg-muted text-ink-2',
                accent: 'border-transparent bg-primary/12 text-primary',
                success: 'border-transparent bg-success/14 text-success',
                warning: 'border-transparent bg-warning/16 text-warning',
                danger: 'border-transparent bg-destructive/12 text-destructive',
                outline: 'border-border bg-card text-ink-2',
            },
            selected: {
                true: 'border-transparent bg-foreground text-background shadow-(--sh-sm)',
                false: '',
            },
            interactive: {
                true: 'cursor-pointer hover:-translate-y-px hover:border-border active:translate-y-0 active:scale-[0.97]',
                false: '',
            },
        },
        defaultVariants: { tone: 'neutral', selected: false, interactive: false },
    },
);

export interface ChipProps extends React.HTMLAttributes<HTMLElement>, Omit<VariantProps<typeof chipVariants>, 'selected' | 'interactive'> {
    asChild?: boolean;
    icon?: LucideIcon;
    dot?: boolean;
    selected?: boolean;
    interactive?: boolean;
}

/** A small pill for status, filters and metadata. Use `asChild` to render a link or button. */
function Chip({ className, tone, selected = false, interactive = false, asChild = false, icon: Icon, dot = false, children, ...props }: ChipProps) {
    const Comp = asChild ? Slot : 'span';

    return (
        <Comp className={cn(chipVariants({ tone, selected, interactive: interactive || asChild }), className)} {...props}>
            {asChild ? (
                children
            ) : (
                <>
                    {dot && <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />}
                    {Icon && <Icon strokeWidth={1.75} />}
                    {children}
                </>
            )}
        </Comp>
    );
}

export { Chip, chipVariants };
