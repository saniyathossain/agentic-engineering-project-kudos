import { type SpaceTheme } from '@/types';

export interface ThemeClasses {
    surface: string;
    text: string;
    muted: string;
    accent: string;
    button: string;
    input: string;
}

export const THEME_CLASSES: Record<SpaceTheme, ThemeClasses> = {
    light: {
        surface: 'bg-white border-neutral-200',
        text: 'text-neutral-900',
        muted: 'text-neutral-600',
        accent: 'text-amber-500',
        button: 'bg-neutral-900 text-white hover:bg-neutral-700',
        input: 'bg-white border-neutral-300 text-neutral-900 placeholder:text-neutral-400',
    },
    dark: {
        surface: 'bg-neutral-900 border-neutral-700',
        text: 'text-neutral-50',
        muted: 'text-neutral-400',
        accent: 'text-amber-400',
        button: 'bg-white text-neutral-900 hover:bg-neutral-200',
        input: 'bg-neutral-800 border-neutral-600 text-neutral-50 placeholder:text-neutral-500',
    },
    brand: {
        surface: 'bg-indigo-50 border-indigo-200',
        text: 'text-indigo-950',
        muted: 'text-indigo-800',
        accent: 'text-amber-500',
        button: 'bg-indigo-600 text-white hover:bg-indigo-500',
        input: 'bg-white border-indigo-300 text-indigo-950 placeholder:text-indigo-300',
    },
};
