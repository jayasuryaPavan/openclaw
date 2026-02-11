import { createHash } from "node:crypto";
import { promises as fs, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, "..");
const HASH_FILE = path.join(ROOT_DIR, "src/canvas-host/a2ui/.bundle.hash");
const OUTPUT_FILE = path.join(ROOT_DIR, "src/canvas-host/a2ui/a2ui.bundle.js");
const A2UI_RENDERER_DIR = path.join(ROOT_DIR, "vendor/a2ui/renderers/lit");
const A2UI_APP_DIR = path.join(ROOT_DIR, "apps/shared/OpenClawKit/Tools/CanvasA2UI");

async function main() {
    // Check if sources exist
    if (!existsSync(A2UI_RENDERER_DIR) || !existsSync(A2UI_APP_DIR)) {
        console.log("A2UI sources missing; keeping prebuilt bundle.");
        return;
    }

    const inputs = [
        path.join(ROOT_DIR, "package.json"),
        path.join(ROOT_DIR, "pnpm-lock.yaml"),
        A2UI_RENDERER_DIR,
        A2UI_APP_DIR,
    ];

    const currentHash = await computeHash(inputs);

    let previousHash = "";
    if (existsSync(HASH_FILE)) {
        previousHash = (await fs.readFile(HASH_FILE, "utf-8")).trim();
    }

    if (previousHash === currentHash && existsSync(OUTPUT_FILE)) {
        console.log("A2UI bundle up to date; skipping.");
        return;
    }

    console.log("A2UI bundle stale; rebuilding...");

    try {
        console.log("Running tsc...");
        execSync(`pnpm exec tsc -p "${A2UI_RENDERER_DIR}/tsconfig.json"`, { stdio: "inherit", cwd: ROOT_DIR });

        console.log("Running rolldown...");
        execSync(`pnpm exec rolldown -c "${A2UI_APP_DIR}/rolldown.config.mjs"`, { stdio: "inherit", cwd: ROOT_DIR });

        // Update hash
        await fs.writeFile(HASH_FILE, currentHash);
        console.log("A2UI bundle updated.");
    } catch (error) {
        console.error("A2UI bundling failed.");
        process.exit(1);
    }
}

async function computeHash(inputs) {
    const files = [];

    async function walk(entryPath) {
        const st = await fs.stat(entryPath);
        if (st.isDirectory()) {
            const entries = await fs.readdir(entryPath);
            for (const entry of entries) {
                await walk(path.join(entryPath, entry));
            }
            return;
        }
        files.push(entryPath);
    }

    for (const input of inputs) {
        if (existsSync(input)) {
            await walk(input);
        }
    }

    // Normalize paths for consistent ordering
    function normalize(p) {
        return p.split(path.sep).join("/");
    }

    files.sort((a, b) => normalize(a).localeCompare(normalize(b)));

    const hash = createHash("sha256");
    for (const filePath of files) {
        const rel = normalize(path.relative(ROOT_DIR, filePath));
        hash.update(rel);
        hash.update("\0");
        const content = await fs.readFile(filePath);
        hash.update(content);
        hash.update("\0");
    }

    return hash.digest("hex");
}

main();
