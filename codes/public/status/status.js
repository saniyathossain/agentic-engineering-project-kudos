/* Shared by the Blade error page and the static outage page. No dependencies; works with the app down.
 * - applies the saved light/dark choice
 * - fills [data-i18n] text from /status/lang.json (static outage page)
 * - [data-poll]: checks /readyz with exponential backoff and reloads when the app answers
 * - [data-copy]: copies the diagnostic details */
(function () {
    'use strict';

    var root = document.documentElement;
    var saved = null;
    try { saved = localStorage.getItem('appearance'); } catch (e) { /* storage blocked: follow the system */ }
    var dark = saved === 'dark' || ((saved === null || saved === 'system') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    root.classList.toggle('dark', dark);

    var FALLBACK = { first_ms: 4000, longest_ms: 15000 };

    function json(url) {
        return fetch(url, { cache: 'no-store', credentials: 'same-origin' }).then(function (r) { return r.json(); });
    }

    function translate(lang) {
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            var value = lang[el.getAttribute('data-i18n')];
            if (value) { el.textContent = value; }
        });
    }

    function format(template, values) {
        return template.replace(/:(\w+)/g, function (_, k) { return values[k] === undefined ? ':' + k : values[k]; });
    }

    function poll(page, lang, config) {
        var pause = config.first_ms;
        var since = Date.now();
        var checks = 0;
        var timer = null;
        var tick = null;
        var label = page.querySelector('[data-next]');
        var downFor = page.querySelector('[data-down-for]');
        var checksEl = page.querySelector('[data-checks]');
        var appRow = page.querySelector('[data-row="app"]');
        var connRow = page.querySelector('[data-row="connection"]');
        var edgeRow = page.querySelector('[data-row="edge"]');
        var button = page.querySelector('[data-check-now]');
        var next = 0;

        function set(row, up) { if (row) { row.setAttribute('data-up', String(up)); var s = row.querySelector('.state'); if (s && lang) { s.textContent = lang[up === true ? 'outage.state.up' : 'outage.state.down'] || s.textContent; } } }

        function render() {
            if (downFor) { downFor.textContent = Math.max(0, Math.round((Date.now() - since) / 1000)) + ' s'; }
            if (checksEl) { checksEl.textContent = String(checks); }
            if (label) {
                var left = Math.max(0, Math.ceil((next - Date.now()) / 1000));
                label.textContent = lang && lang['status.next_check'] ? format(lang['status.next_check'], { seconds: left }) : left + ' s';
            }
        }

        function schedule() {
            next = Date.now() + pause;
            clearTimeout(timer);
            timer = setTimeout(check, pause);
            pause = Math.min(pause * 2, config.longest_ms);
        }

        function check() {
            clearTimeout(timer);
            checks += 1;
            set(connRow, navigator.onLine);
            if (label && lang) { label.textContent = lang['status.checking'] || '…'; }
            fetch('/readyz', { cache: 'no-store', credentials: 'same-origin' })
                .then(function (r) {
                    set(appRow, r.ok);
                    if (r.ok) {
                        if (label && lang) { label.textContent = lang['status.back_online'] || ''; }
                        window.location.assign(page.getAttribute('data-return') || '/');
                        return;
                    }
                    schedule();
                })
                .catch(function () { set(appRow, false); schedule(); });
        }

        set(connRow, navigator.onLine);
        set(edgeRow, true);
        set(appRow, false);
        window.addEventListener('online', check);
        if (button) { button.addEventListener('click', check); }
        tick = setInterval(render, 500);
        render();
        schedule();
        window.addEventListener('pagehide', function () { clearInterval(tick); clearTimeout(timer); });
    }

    function copy(button) {
        var text = button.getAttribute('data-copy');
        var done = button.getAttribute('data-done');
        var label = button.querySelector('span');
        var finish = function () { if (label && done) { var old = label.textContent; label.textContent = done; setTimeout(function () { label.textContent = old; }, 1800); } };
        if (navigator.clipboard) { navigator.clipboard.writeText(text).then(finish, finish); } else { finish(); }
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-copy]').forEach(function (b) { b.addEventListener('click', function () { copy(b); }); });
        document.querySelectorAll('[data-reload]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); window.location.reload(); }); });
        var page = document.querySelector('[data-poll]');
        var needsLang = document.querySelector('[data-i18n]') !== null;

        Promise.all([
            needsLang || page ? json('/status/lang.json').catch(function () { return null; }) : Promise.resolve(null),
            page ? json('/status/outage-config.json').catch(function () { return FALLBACK; }) : Promise.resolve(null),
        ]).then(function (loaded) {
            if (loaded[0] && needsLang) { translate(loaded[0]); }
            if (page) { poll(page, loaded[0], loaded[1] || FALLBACK); }
        });
    });
})();
