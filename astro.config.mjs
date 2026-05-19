import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  site: "https://alieron.github.io",
  base: "/alieron",
  outDir: "./dist",
  vite: {
    plugins: [tailwindcss()],
  },
});
