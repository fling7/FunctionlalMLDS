import { defineConfig, transformWithEsbuild } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";
import { cp, rm } from "node:fs/promises";

function unityBuildPlugin() {
  return {
    name: "unity-build",
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const pathname = request.url?.split("?", 1)[0] ?? "";
        if (pathname.startsWith("/BuildOutput/") && pathname.endsWith(".br")) {
          response.setHeader("Content-Encoding", "br");
          if (pathname.endsWith(".wasm.br")) {
            response.setHeader("Content-Type", "application/wasm");
          } else if (pathname.endsWith(".js.br")) {
            response.setHeader("Content-Type", "text/javascript; charset=utf-8");
          } else {
            response.setHeader("Content-Type", "application/octet-stream");
          }
        }
        next();
      });
    },
    async closeBundle() {
      const target = resolve(__dirname, "dist", "BuildOutput");
      await rm(target, { recursive: true, force: true });
      await cp(resolve(__dirname, "BuildOutput"), target, { recursive: true });
    },
  };
}

export default defineConfig({
  server: {
    https: {
      key: "./keys/localhost-key.pem",
      cert: "./keys/localhost-cert.pem",
    },
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:3001",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [
    {
      name: "treat-js-files-as-jsx",
      async transform(code, id) {
        if (!id.match(/src\/.*\.js$/)) return null;

        return transformWithEsbuild(code, id, {
          loader: "jsx",
          jsx: "automatic",
        });
      },
    },
    react(),
    unityBuildPlugin(),
  ],

  optimizeDeps: {
    force: true,
    esbuildOptions: {
      loader: {
        ".js": "jsx",
      },
    },
  },
  build: {
    rollupOptions: {
      input: {
        survey: resolve(__dirname, "index.html"),
        admin: resolve(__dirname, "admin.html"),
      },
    },
  },
});
