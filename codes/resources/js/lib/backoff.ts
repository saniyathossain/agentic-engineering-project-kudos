/** Exponential backoff: first, then doubling, never longer than `longest` (both milliseconds). */
export function createBackoff(first: number, longest: number): { next: () => number; reset: () => void } {
    let pause = first;

    return {
        next: () => {
            const current = pause;
            pause = Math.min(pause * 2, longest);

            return current;
        },
        reset: () => {
            pause = first;
        },
    };
}
