import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  return {
    base: "./",
    resolve: {
      alias: {
        "@": resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "0.0.0.0",
      port: 8080,
      hmr: true,
      open: false,
      proxy: {
        [env.VITE_API_BASE_URL]: {
          target: env.VITE_PROXY_TARGET,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
    plugins: [react()],
  };
});
