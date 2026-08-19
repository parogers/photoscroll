import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
    base: './',
    server: {
        allowedHosts: [
            'nebula-sizable-dude.ngrok-free.dev',
        ],
    },
    plugins: [vue()],
})
