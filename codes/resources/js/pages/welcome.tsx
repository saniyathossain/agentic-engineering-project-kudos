import { Button } from '@/components/ui/button';
import { type SharedData } from '@/types';
import { Head, Link, usePage } from '@inertiajs/react';

const FEATURES: ReadonlyArray<{ title: string; text: string }> = [
    { title: 'Collect', text: 'Share one themed link. Respondents send text testimonials with a star rating - no account needed.' },
    { title: 'Curate', text: 'Review everything in an inbox: publish, hide, favorite, edit.' },
    { title: 'Showcase', text: 'Drop an embeddable wall of love on your site with one iframe.' },
];

export default function Welcome() {
    const { auth, name } = usePage<SharedData>().props;

    return (
        <>
            <Head title="Collect and showcase customer love" />
            <main className="mx-auto flex min-h-svh max-w-4xl flex-col justify-center gap-10 px-6 py-16">
                <header className="space-y-4">
                    <p className="text-muted-foreground text-sm font-medium tracking-wide uppercase">{name}</p>
                    <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Turn happy customers into your best marketing.</h1>
                    <p className="text-muted-foreground max-w-2xl text-lg">A minimal testimonial platform: create a space, collect testimonials, publish the best ones.</p>
                    <div className="flex gap-3">
                        {auth.user ? (
                            <Button asChild>
                                <Link href={route('dashboard')}>Go to dashboard</Link>
                            </Button>
                        ) : (
                            <>
                                <Button asChild>
                                    <Link href={route('register')}>Get started free</Link>
                                </Button>
                                <Button asChild variant="outline">
                                    <Link href={route('login')}>Log in</Link>
                                </Button>
                            </>
                        )}
                    </div>
                </header>

                <section className="grid gap-6 sm:grid-cols-3" aria-label="Features">
                    {FEATURES.map(({ title, text }) => (
                        <article key={title} className="rounded-xl border p-5">
                            <h2 className="mb-2 text-lg font-semibold">{title}</h2>
                            <p className="text-muted-foreground text-sm">{text}</p>
                        </article>
                    ))}
                </section>
            </main>
        </>
    );
}
