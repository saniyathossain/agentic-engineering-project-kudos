import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { addDays, addMonths, type DayKey, formatDay, fromDayKey, monthGrid, startOfMonth, toDayKey } from '@/lib/dates';
import { cn } from '@/lib/utils';
import { CalendarDays, ChevronLeft, ChevronRight, X } from 'lucide-react';
import { type KeyboardEvent, useEffect, useRef, useState } from 'react';

interface DatePickerProps {
    value: DayKey | null;
    onChange: (value: DayKey | null) => void;
    label: string;
    placeholder?: string;
    min?: DayKey;
    max?: DayKey;
    className?: string;
}

const WEEKDAYS = Array.from({ length: 7 }, (_, index) => new Intl.DateTimeFormat(undefined, { weekday: 'narrow' }).format(new Date(2026, 0, 4 + index)));
const MONTH_FORMAT = new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' });

/** A light date picker: a popover month grid with keyboard navigation. No dependencies, nothing rendered until opened. */
export default function DatePicker({ value, onChange, label, placeholder = 'Pick a date', min, max, className }: DatePickerProps) {
    const [open, setOpen] = useState(false);
    const [view, setView] = useState<Date>(() => startOfMonth(value ? fromDayKey(value) : new Date()));
    const [focusKey, setFocusKey] = useState<DayKey>(value ?? toDayKey(new Date()));
    const gridRef = useRef<HTMLDivElement>(null);
    const today = toDayKey(new Date());

    const handleOpenChange = (next: boolean) => {
        if (next) {
            const target = value ?? today;
            setView(startOfMonth(fromDayKey(target)));
            setFocusKey(target);
        }
        setOpen(next);
    };

    useEffect(() => {
        if (open) {
            gridRef.current?.querySelector<HTMLButtonElement>(`[data-day="${focusKey}"]`)?.focus();
        }
    }, [focusKey, view, open]);

    const isDisabled = (key: DayKey): boolean => (min !== undefined && key < min) || (max !== undefined && key > max);

    const select = (key: DayKey) => {
        if (isDisabled(key)) {
            return;
        }
        onChange(key);
        setOpen(false);
    };

    const move = (event: KeyboardEvent, days: number) => {
        event.preventDefault();
        const next = addDays(fromDayKey(focusKey), days);
        setFocusKey(toDayKey(next));
        setView(startOfMonth(next));
    };

    const onKeyDown = (event: KeyboardEvent) => {
        const steps: Record<string, number> = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
        if (event.key in steps) {
            move(event, steps[event.key]);
        }
    };

    return (
        <div className={cn('flex items-center gap-1', className)}>
            <Popover open={open} onOpenChange={handleOpenChange}>
                <PopoverTrigger asChild>
                    <Button type="button" variant="outline" size="sm" aria-label={`${label}: ${value ? formatDay(value) : 'not set'}`} className={cn('justify-start font-normal', !value && 'text-ink-3')}>
                        <CalendarDays strokeWidth={1.75} className="ico-calendar" />
                        {value ? formatDay(value) : placeholder}
                    </Button>
                </PopoverTrigger>
                <PopoverContent aria-label={label} className="w-72">
                    <div className="mb-2 flex items-center justify-between">
                        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Previous month" onClick={() => setView(addMonths(view, -1))}>
                            <ChevronLeft strokeWidth={1.75} className="ico-left" />
                        </Button>
                        <p className="font-display text-base font-medium" aria-live="polite">
                            {MONTH_FORMAT.format(view)}
                        </p>
                        <Button type="button" variant="ghost" size="icon" className="size-8" aria-label="Next month" onClick={() => setView(addMonths(view, 1))}>
                            <ChevronRight strokeWidth={1.75} className="ico-right" />
                        </Button>
                    </div>
                    <div className="text-ink-3 grid grid-cols-7 text-center text-xs font-medium" aria-hidden="true">
                        {WEEKDAYS.map((day, index) => (
                            <span key={index} className="py-1">
                                {day}
                            </span>
                        ))}
                    </div>
                    <div ref={gridRef} role="grid" aria-label={MONTH_FORMAT.format(view)} className="grid grid-cols-7 gap-0.5" onKeyDown={onKeyDown}>
                        {monthGrid(view).map((date) => {
                            const key = toDayKey(date);
                            const inMonth = date.getMonth() === view.getMonth();
                            const selected = key === value;

                            return (
                                <button
                                    key={key}
                                    type="button"
                                    role="gridcell"
                                    data-day={key}
                                    tabIndex={key === focusKey ? 0 : -1}
                                    aria-selected={selected}
                                    aria-label={formatDay(key, { dateStyle: 'full' })}
                                    disabled={isDisabled(key)}
                                    onClick={() => select(key)}
                                    className={cn(
                                        'size-9 rounded-xl text-sm tabular-nums transition-[background-color,color,transform] duration-150 hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/35 focus-visible:outline-hidden active:scale-95 disabled:pointer-events-none disabled:opacity-30',
                                        !inMonth && 'text-ink-3',
                                        key === today && !selected && 'ring-1 ring-primary/50',
                                        selected && 'bg-primary text-primary-foreground shadow-(--lift) hover:bg-primary',
                                    )}
                                >
                                    {date.getDate()}
                                </button>
                            );
                        })}
                    </div>
                    <div className="mt-2 flex justify-between border-t pt-2">
                        <Button type="button" variant="ghost" size="sm" onClick={() => select(today)} disabled={isDisabled(today)}>
                            Today
                        </Button>
                        <Button type="button" variant="ghost" size="sm" onClick={() => { onChange(null); setOpen(false); }} disabled={value === null}>
                            Clear
                        </Button>
                    </div>
                </PopoverContent>
            </Popover>
            {value && (
                <Button type="button" variant="ghost" size="icon" className="size-8" aria-label={`Clear ${label}`} onClick={() => onChange(null)}>
                    <X strokeWidth={1.75} />
                </Button>
            )}
        </div>
    );
}
