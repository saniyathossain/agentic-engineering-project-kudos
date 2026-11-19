import { type SpaceTheme } from '@/types';

/** Space themes belong to the space owner, so they do not follow the app's light/dark mode. */
export interface ThemeClasses {
    page: string;
    surface: string;
    text: string;
    muted: string;
    star: string;
    button: string;
    input: string;
    divider: string;
}

export const THEME_CLASSES: Record<SpaceTheme, ThemeClasses> = {
    light: {
        page: 'bg-[oklch(0.975_0.011_78)] [background-image:radial-gradient(48rem_30rem_at_85%_-10%,oklch(0.93_0.05_70/0.6),transparent_70%)]',
        surface:
            'bg-[oklch(0.995_0.004_80)] border-[oklch(0.3_0.03_55/0.12)] shadow-[0_1px_0_oklch(1_0_0),0_24px_48px_-24px_oklch(0.3_0.04_50/0.25)]',
        text: 'text-[oklch(0.22_0.02_50)]',
        muted: 'text-[oklch(0.46_0.02_55)]',
        star: 'text-[oklch(0.78_0.16_78)]',
        button: 'bg-[oklch(0.54_0.18_35)] text-white hover:brightness-105',
        input: 'bg-white border-[oklch(0.3_0.03_55/0.2)] text-[oklch(0.22_0.02_50)] placeholder:text-[oklch(0.6_0.02_55)] focus-visible:border-[oklch(0.54_0.18_35)] focus-visible:ring-[oklch(0.54_0.18_35/0.25)]',
        divider: 'border-[oklch(0.3_0.03_55/0.12)]',
    },
    dark: {
        page: 'bg-[oklch(0.17_0.013_55)] [background-image:radial-gradient(48rem_30rem_at_85%_-10%,oklch(0.34_0.07_40/0.4),transparent_70%)]',
        surface: 'bg-[oklch(0.24_0.013_55)] border-white/10 shadow-[inset_0_1px_0_oklch(1_0_0/0.1),0_24px_48px_-24px_oklch(0_0_0/0.7)]',
        text: 'text-[oklch(0.95_0.008_78)]',
        muted: 'text-[oklch(0.74_0.012_70)]',
        star: 'text-[oklch(0.82_0.15_82)]',
        button: 'bg-[oklch(0.74_0.15_40)] text-[oklch(0.2_0.03_45)] hover:brightness-105',
        input: 'bg-[oklch(0.2_0.013_55)] border-white/16 text-[oklch(0.95_0.008_78)] placeholder:text-[oklch(0.6_0.012_70)] focus-visible:border-[oklch(0.74_0.15_40)] focus-visible:ring-[oklch(0.74_0.15_40/0.3)]',
        divider: 'border-white/10',
    },
    brand: {
        page: 'bg-[oklch(0.6_0.14_40)] [background-image:radial-gradient(48rem_30rem_at_15%_-10%,oklch(0.7_0.15_55/0.55),transparent_70%)]',
        surface: 'bg-[oklch(0.985_0.012_60)] border-[oklch(0.85_0.06_50)] shadow-[0_24px_48px_-20px_oklch(0.3_0.1_35/0.55)]',
        text: 'text-[oklch(0.26_0.05_40)]',
        muted: 'text-[oklch(0.42_0.05_40)]',
        star: 'text-[oklch(0.74_0.16_75)]',
        button: 'bg-[oklch(0.42_0.14_35)] text-white hover:brightness-110',
        input: 'bg-white border-[oklch(0.8_0.06_50)] text-[oklch(0.26_0.05_40)] placeholder:text-[oklch(0.6_0.04_45)] focus-visible:border-[oklch(0.42_0.14_35)] focus-visible:ring-[oklch(0.42_0.14_35/0.25)]',
        divider: 'border-[oklch(0.85_0.06_50)]',
    },
};
