import { Star } from 'lucide-react';

interface StarRatingProps {
    rating: number;
}

const MAX_STARS = 5;

export default function StarRating({ rating }: StarRatingProps) {
    return (
        <div className="flex gap-0.5" role="img" aria-label={`${rating} out of ${MAX_STARS} stars`}>
            {Array.from({ length: MAX_STARS }, (_, index) => (
                <Star key={index} className={`size-4 ${index < rating ? 'fill-amber-400 text-amber-400' : 'text-current opacity-25'}`} />
            ))}
        </div>
    );
}
