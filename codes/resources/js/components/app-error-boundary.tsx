import { t } from '@/lib/i18n';
import { log } from '@/lib/logger';
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface State {
    failed: boolean;
}

/** Last line of defence for render errors: report them, and show a calm card instead of a blank page. */
export default class AppErrorBoundary extends Component<{ children: ReactNode }, State> {
    state: State = { failed: false };

    static getDerivedStateFromError(): State {
        return { failed: true };
    }

    componentDidCatch(error: Error, info: ErrorInfo): void {
        log.error(
            `${error.name}: ${error.message}`,
            { stack: error.stack?.split('\n').slice(0, 8).join('\n'), component_stack: info.componentStack?.split('\n').slice(0, 8).join('\n') },
            'react.boundary',
        );
    }

    render(): ReactNode {
        if (!this.state.failed) {
            return this.props.children;
        }

        return (
            <main className="flex min-h-svh items-center justify-center p-4">
                <div role="alert" className="pane rise w-full max-w-md rounded-3xl p-8 text-center">
                    <h1 className="font-display text-2xl font-medium">{t('boundary.title')}</h1>
                    <p className="text-ink-2 mt-2 text-sm">{t('boundary.body')}</p>
                    <button
                        type="button"
                        onClick={() => window.location.reload()}
                        className="bg-primary text-primary-foreground mt-6 h-10 rounded-xl px-5 text-sm font-medium shadow-(--lift)"
                    >
                        {t('boundary.reload')}
                    </button>
                </div>
            </main>
        );
    }
}
