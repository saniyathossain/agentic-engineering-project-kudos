import * as React from 'react';

import { cn } from '@/lib/utils';

const Textarea = React.forwardRef<HTMLTextAreaElement, React.ComponentProps<'textarea'>>(({ className, ...props }, ref) => (
    <textarea
        ref={ref}
        className={cn(
            'border-input placeholder:text-muted-foreground focus-visible:ring-ring flex min-h-24 w-full rounded-xl border border-input bg-background/60 px-3 py-2 text-sm shadow-xs transition-[border-color,box-shadow] duration-200 focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/25 focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50',
            className,
        )}
        {...props}
    />
));
Textarea.displayName = 'Textarea';

export { Textarea };
