import { type Appearance, useAppearance } from '@/hooks/use-appearance';
import { t } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { Monitor, Moon, Sun } from 'lucide-react';

const OPTIONS: ReadonlyArray<{ value: Appearance; icon: typeof Sun; anim: string }> = [
    { value: 'light', icon: Sun, anim: 'ico-sun' },
    { value: 'dark', icon: Moon, anim: 'ico-moon' },
    { value: 'system', icon: Monitor, anim: '' },
];

/** Three-way light / dark / system switch as a small segmented control. */
export default function ThemeSwitch() {
    const { appearance, updateAppearance } = useAppearance();

    return (
        <div role="radiogroup" aria-label={t('footer.group.appearance')} className="bg-muted inline-flex rounded-xl p-1">
            {OPTIONS.map(({ value, icon: Icon, anim }) => {
                const label = t(`footer.theme.${value}`);

                return (
                    <button
                        key={value}
                        type="button"
                        role="radio"
                        aria-checked={appearance === value}
                        aria-label={label}
                        title={label}
                        onClick={() => updateAppearance(value)}
                        className={cn(
                            'flex size-8 items-center justify-center rounded-lg transition-[background-color,color,box-shadow] duration-200',
                            appearance === value ? 'bg-primary/15 text-primary shadow-(--sh-sm)' : 'text-ink-3 hover:text-foreground',
                        )}
                    >
                        <Icon className={cn('size-4', anim)} strokeWidth={1.75} />
                    </button>
                );
            })}
        </div>
    );
}
