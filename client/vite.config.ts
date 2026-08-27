import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import packageJSON from './package.json' with { type: 'json' };

// https://vite.dev/config/
export default defineConfig({
    base: './',
    server: {
        allowedHosts: [
            'nebula-sizable-dude.ngrok-free.dev',
        ],
    },
    plugins: [vue()],
    define: {
        'import.meta.env.APP_VERSION': JSON.stringify(packageJSON.version),
    },
})
