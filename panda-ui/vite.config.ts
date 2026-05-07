import { defineConfig } from "vite";

export default defineConfig({
  base: "/panda/",
  build: {
    outDir: "../dist/panda-ui",
    emptyOutDir: true,
  },
});
