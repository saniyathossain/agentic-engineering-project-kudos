import process from 'node:process';
import react from '@vitejs/plugin-react';
import laravel from 'laravel-vite-plugin';
import {
    defineConfig
} from 'vite';
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    plugins: [
        laravel({
            input: ['resources/css/app.css', 'resources/js/app.tsx'],
            ssr: 'resources/js/ssr.jsx',
            refresh: true,
        }),
        react(),
        tailwindcss(),
    ],
    server: {
        // the browser reaches the dev server through the published host port, not the container's 5173
        origin: process.env.VITE_DEV_ORIGIN,
        cors: true,
    },
    esbuild: {
        jsx: 'automatic',
    },
});