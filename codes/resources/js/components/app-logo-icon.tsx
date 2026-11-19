import { SVGAttributes } from 'react';

/** Kudos mark: a pair of quotation marks. */
export default function AppLogoIcon(props: SVGAttributes<SVGElement>) {
    return (
        <svg {...props} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M7.2 5.5C4.7 6.7 3.2 8.9 3.2 12v5.5h6.3v-5.7H6.6c.1-1.6.8-2.7 2.2-3.5L7.2 5.5Zm9.6 0c-2.5 1.2-4 3.4-4 6.5v5.5h6.3v-5.7h-2.9c.1-1.6.8-2.7 2.2-3.5l-1.6-2.8Z" />
        </svg>
    );
}
