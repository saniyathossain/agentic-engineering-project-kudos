import AppLogoIcon from '@/components/app-logo-icon';
import AppearanceToggleDropdown from '@/components/appearance-dropdown';
import StarRating from '@/components/star-rating';
import { Button } from '@/components/ui/button';
import { type SharedData } from '@/types';
import { Head, Link, usePage } from '@inertiajs/react';
import { ArrowRight, Code2, Inbox, Link2, type LucideIcon } from 'lucide-react';
import { type CSSProperties } from 'react';

interface Feature {
    title: string;
    text: string;
    icon: LucideIcon;
}

const FEATURES: readonly Feature[] = [
    { title: 'Collect', text: 'Share one themed link. People write two sentences and a star rating. No account.', icon: Link2 },
    { title: 'Curate', text: 'Everything lands in an inbox. Publish the good ones, hide the rest, fix a typo.', icon: Inbox },
    { title: 'Show', text: 'One iframe puts a wall of published testimonials on any page of your site.', icon: Code2 },
];

interface SampleQuote {
    body: string;
    name: string;
    role: string;
    rating: number;
    tilt: string;
}

const SAMPLES: readonly SampleQuote[] = [
    {
        body: 'We finally have real words from real customers on our pricing page.',
        name: 'Maya Chen',
        role: 'Founder, Tilework',
        rating: 5,
        tilt: '-2deg',
    },
    {
        body: 'Setup took five minutes. The wall embed matched our site on the first try.',
        name: 'Ravi Patel',
        role: 'Designer',
        rating: 5,
        tilt: '1.5deg',
    },
];

export default function Welcome() {
    const { auth, name } = usePage<SharedData>().props;

    return (
        <>
            <Head title="Collect and show customer testimonials" />
            <div className="mx-auto flex min-h-svh w-full max-w-6xl flex-col px-5 sm:px-8">
                <nav className="flex items-center justify-between py-5" aria-label="Main">
                    <Link href={route('home')} className="flex items-center gap-2.5">
                        <span className="bg-primary text-primary-foreground flex size-9 items-center justify-center rounded-xl shadow-(--lift)">
                            <AppLogoIcon className="size-5 fill-current" />
                        </span>
                        <span className="font-display text-xl font-semibold">{name}</span>
                    </Link>
                    <div className="flex items-center gap-1">
                        <AppearanceToggleDropdown />
                        {auth.user ? (
                            <Button asChild size="sm">
                                <Link href={route('dashboard')}>Dashboard</Link>
                            </Button>
                        ) : (
                            <>
                                <Button asChild size="sm" variant="ghost">
                                    <Link href={route('login')}>Log in</Link>
                                </Button>
                                <Button asChild size="sm">
                                    <Link href={route('register')}>Start free</Link>
                                </Button>
                            </>
                        )}
                    </div>
                </nav>

                <main className="grid flex-1 items-center gap-12 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:py-20">
                    <section className="space-y-6">
                        <p className="rise text-primary text-sm font-medium tracking-wide uppercase">Testimonials, without the tooling</p>
                        <h1 className="rise font-display text-5xl leading-[1.05] font-medium sm:text-6xl" style={{ '--i': 1 } as CSSProperties}>
                            Let your customers do the talking.
                        </h1>
                        <p className="rise text-muted-foreground max-w-lg text-lg leading-relaxed" style={{ '--i': 2 } as CSSProperties}>
                            Send one link, collect testimonials, publish the best ones on your site. Free for one space.
                        </p>
                        <div className="rise flex flex-wrap gap-3" style={{ '--i': 3 } as CSSProperties}>
                            <Button asChild size="lg">
                                <Link href={auth.user ? route('dashboard') : route('register')}>
                                    {auth.user ? 'Open dashboard' : 'Create your first space'} <ArrowRight strokeWidth={1.75} className="ico-right" />
                                </Link>
                            </Button>
                            {!auth.user && (
                                <Button asChild size="lg" variant="outline">
                                    <Link href={route('login')}>Log in</Link>
                                </Button>
                            )}
                        </div>
                    </section>

                    <section className="relative mx-auto flex w-full max-w-md flex-col gap-5" aria-label="Example testimonials">
                        {SAMPLES.map((sample, index) => (
                            <figure
                                key={sample.name}
                                className="glass animate-float rounded-3xl p-6"
                                style={
                                    { '--tilt': sample.tilt, animationDelay: `${index * -4}s`, marginLeft: index === 1 ? '2rem' : 0 } as CSSProperties
                                }
                            >
                                <StarRating value={sample.rating} />
                                <blockquote className="font-display mt-3 text-xl leading-snug">{sample.body}</blockquote>
                                <figcaption className="mt-4 text-sm">
                                    <span className="font-semibold">{sample.name}</span>{' '}
                                    <span className="text-muted-foreground">· {sample.role}</span>
                                </figcaption>
                            </figure>
                        ))}
                    </section>
                </main>

                <section className="grid gap-4 pb-16 sm:grid-cols-3" aria-label="How it works">
                    {FEATURES.map(({ title, text, icon: Icon }, index) => (
                        <article key={title} className="pane rise rounded-2xl p-6" style={{ '--i': index + 4 } as CSSProperties}>
                            <span className="icon-chip mb-4">
                                <Icon className="size-[18px]" strokeWidth={1.75} />
                            </span>
                            <h2 className="font-display text-xl font-medium">{title}</h2>
                            <p className="text-muted-foreground mt-1.5 text-sm leading-relaxed">{text}</p>
                        </article>
                    ))}
                </section>
            </div>
        </>
    );
}
