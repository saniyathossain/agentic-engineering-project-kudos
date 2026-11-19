import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import reactHooks from 'eslint-plugin-react-hooks';
import globals from 'globals';
import typescript from 'typescript-eslint';

/**
 * ESLint 10 flat config. eslint-plugin-react does not support ESLint 10, and the automatic JSX runtime plus
 * TypeScript already cover what it checked, so only the React Hooks rules are kept.
 *
 * @type {import('eslint').Linter.Config[]}
 */
export default [
    js.configs.recommended,
    ...typescript.configs.recommended,
    reactHooks.configs.flat.recommended,
    {
        languageOptions: {
            globals: {
                ...globals.browser,
            },
        },
    },
    {
        ignores: ['vendor', 'node_modules', 'public', 'bootstrap/ssr', 'tailwind.config.js'],
    },
    prettier, // Turn off all rules that might conflict with Prettier
];
