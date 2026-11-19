import * as React from 'react';

import { cn } from '@/lib/utils';

const Textarea = React.forwardRef<HTMLTextAreaElement, React.ComponentProps<'textarea'>>(({ className, ...props }, ref) => (
    <textarea
        ref={ref}
        className={cn(
            'field flex min-h-24 w-full rounded-xl px-3 py-2 text-sm placeholder:text-muted-foreground',
            className,
        )}
        {...props}
    />
));
Textarea.displayName = 'Textarea';

export { Textarea };
