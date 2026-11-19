import en from '@lang/en.json';

/** lang/en.json is the single source: Laravel reads it with __(), the React app imports it here. */
export type TranslationKey = keyof typeof en;
export type TranslationParams = Record<string, string | number>;

const catalogs = import.meta.glob<Record<string, string>>('../../../lang/*.json', { import: 'default' });

let active: Record<string, string> = en;
let current = 'en';

/** Loads a locale's catalog (English fills any gaps). Unknown locales keep English. */
export async function setLocale(locale: string): Promise<void> {
    if (locale === 'en') {
        active = en;
        current = 'en';

        return;
    }

    const load = catalogs[`../../../lang/${locale}.json`];
    if (load === undefined) {
        return;
    }

    active = { ...en, ...(await load()) };
    current = locale;
}

export const currentLocale = (): string => current;

const fill = (template: string, params?: TranslationParams): string =>
    params ? template.replace(/:(\w+)/g, (match, name: string) => (name in params ? String(params[name]) : match)) : template;

/** Translate a key; `:name` placeholders are replaced from params, like Laravel's __(). */
export function t(key: TranslationKey, params?: TranslationParams): string {
    return fill(active[key] ?? en[key], params);
}

/** Translate a key built at run time (for example `status.title.${code}`); falls back to the key itself. */
export function tDynamic(key: string, params?: TranslationParams): string {
    return fill(active[key] ?? (en as Record<string, string>)[key] ?? key, params);
}

/** Plural helper: uses `<key>.one` for 1 and `<key>.other` otherwise, with :count available. */
export function tc(key: string, count: number, params?: TranslationParams): string {
    return tDynamic(`${key}.${count === 1 ? 'one' : 'other'}`, { count, ...params });
}
