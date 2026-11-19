import { cn } from '@/lib/utils';
import { Star } from 'lucide-react';

const MAX_STARS = 5;

interface StarRatingProps {
    value: number | null;
    onChange?: (value: number) => void;
    className?: string;
}

export default function StarRating({ value, onChange, className }: StarRatingProps) {
    const stars = Array.from({ length: MAX_STARS }, (_, index) => index + 1);

    return (
        <div
            className={cn('text-star flex gap-0.5', className)}
            role={onChange ? 'radiogroup' : 'img'}
            aria-label={`Rating: ${value ?? 0} of ${MAX_STARS}`}
        >
            {stars.map((star) => {
                const filled = star <= (value ?? 0);
                const icon = (
                    <Star
                        className={cn(
                            'size-5 transition-transform duration-200',
                            filled ? 'fill-current' : 'opacity-40',
                            onChange && 'hover:scale-110',
                        )}
                        strokeWidth={1.5}
                    />
                );

                return onChange ? (
                    <button
                        key={star}
                        type="button"
                        role="radio"
                        aria-checked={star === value}
                        aria-label={`${star} stars`}
                        onClick={() => onChange(star)}
                        className="rounded-md"
                    >
                        {icon}
                    </button>
                ) : (
                    <span key={star}>{icon}</span>
                );
            })}
        </div>
    );
}
