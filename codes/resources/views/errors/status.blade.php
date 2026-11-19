@php
    /** @var \App\Support\Errors\ErrorPage $page */
    $key = $page->copyKey();
    $transient = $page->transient();
    $polls = $page->polls();
    $details = trim(__('status.error_code', ['code' => $page->status]).' · '.__('status.title.'.$key)
        .($requestId ? "\n".__('status.request_id').': '.$requestId : '')."\n".now()->toIso8601String());
@endphp
<!doctype html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="color-scheme" content="light dark">
    <meta name="robots" content="noindex">
    <title>{{ __('status.title.'.$key) }} - {{ config('app.name') }}</title>
    <link rel="preconnect" href="https://fonts.bunny.net">
    <link href="https://fonts.bunny.net/css?family=instrument-sans:400,500,600|fraunces:500" rel="stylesheet">
    <link rel="stylesheet" href="/status/status.css">
    <script src="/status/status.js"></script>
</head>
<body>
    <main class="card" role="alert" @if($polls) data-poll data-return="{{ request()->isMethod('GET') ? url()->current() : url('/') }}" @endif>
        <span class="chip-icon {{ $transient ? 'calm pulse' : '' }}" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                @if($transient)
                    <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>
                @else
                    <path d="M10.3 3.9 2.4 17.5A2 2 0 0 0 4.1 20.5h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>
                @endif
            </svg>
        </span>
        <div><span class="code">{{ __('status.error_code', ['code' => $page->status]) }}</span></div>
        <h1>{{ __('status.title.'.$key) }}</h1>
        <p>{{ __('status.why.'.$key) }}</p>
        @if($page->dependency)
            <p class="dep">{{ __('status.dependency.'.$page->dependency->value) }}</p>
        @endif
        @if($polls)
            <div class="facts"><span data-next>{{ __('status.checking') }}</span></div>
        @elseif($page->retryAfter)
            <div class="facts"><span>{{ __('status.retry_after', ['seconds' => $page->retryAfter]) }}</span></div>
        @endif
        <div class="actions">
            <a class="btn primary" href="{{ url()->current() }}" data-reload>{{ __('status.action.retry') }}</a>
            <a class="btn" href="/">{{ __('status.action.home') }}</a>
            <button class="btn" type="button" data-copy="{{ $details }}" data-done="{{ __('status.action.copied') }}"><span>{{ __('status.action.copy') }}</span></button>
        </div>
        @if($requestId)
            <p class="meta">{{ __('status.request_id') }}: <code>{{ $requestId }}</code></p>
        @endif
    </main>
</body>
</html>
