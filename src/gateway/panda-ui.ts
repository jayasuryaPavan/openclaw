import type { IncomingMessage, ServerResponse } from "node:http";
import fs from "node:fs";
import path from "node:path";

const PANDA_PATH = "/panda";

function contentTypeForExt(ext: string): string {
  switch (ext) {
    case ".html": return "text/html; charset=utf-8";
    case ".js":   return "application/javascript; charset=utf-8";
    case ".css":  return "text/css; charset=utf-8";
    case ".json": return "application/json; charset=utf-8";
    case ".svg":  return "image/svg+xml";
    case ".png":  return "image/png";
    case ".ico":  return "image/x-icon";
    default:      return "application/octet-stream";
  }
}

function isSafeRelativePath(relPath: string): boolean {
  if (!relPath) return false;
  const normalized = path.posix.normalize(relPath);
  return !normalized.startsWith("../") && normalized !== ".." && !normalized.includes("\0");
}

function resolvePandaUiRoot(): string {
  // Gateway is started from openclaw/ root (start.ps1 does Set-Location $PSScriptRoot)
  return path.join(process.cwd(), "dist", "panda-ui");
}

export interface PandaUiOptions {
  token?: string;
  agentId?: string;
  baseUrl?: string;
}

function injectPandaConfig(html: string, opts: PandaUiOptions): string {
  const { token = "", agentId = "panda", baseUrl = "" } = opts;
  const script =
    `<script>` +
    `window.__PANDA_TOKEN__=${JSON.stringify(token)};` +
    `window.__PANDA_AGENT_ID__=${JSON.stringify(agentId)};` +
    `window.__PANDA_BASE_URL__=${JSON.stringify(baseUrl)};` +
    `</script>`;
  const headClose = html.indexOf("</head>");
  if (headClose !== -1) {
    return `${html.slice(0, headClose)}${script}${html.slice(headClose)}`;
  }
  return `${script}${html}`;
}

function applySecurityHeaders(res: ServerResponse): void {
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("Content-Security-Policy", "frame-ancestors 'none'");
  res.setHeader("X-Content-Type-Options", "nosniff");
}

export function handlePandaUiHttpRequest(
  req: IncomingMessage,
  res: ServerResponse,
  opts?: PandaUiOptions,
): boolean {
  const urlRaw = req.url;
  if (!urlRaw) return false;
  if (req.method !== "GET" && req.method !== "HEAD") return false;

  const url = new URL(urlRaw, "http://localhost");
  const pathname = url.pathname;

  // Handle /panda redirect → /panda/
  if (pathname === PANDA_PATH) {
    applySecurityHeaders(res);
    res.statusCode = 302;
    res.setHeader("Location", `${PANDA_PATH}/`);
    res.end();
    return true;
  }

  if (!pathname.startsWith(`${PANDA_PATH}/`)) return false;

  applySecurityHeaders(res);

  const uiRoot = resolvePandaUiRoot();
  if (!fs.existsSync(uiRoot)) {
    res.statusCode = 503;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.end("Panda UI not built yet. Run: pnpm panda-ui:build");
    return true;
  }

  // Strip /panda/ prefix to get relative path
  const rel = pathname.slice(`${PANDA_PATH}/`.length) || "index.html";
  const filePath = isSafeRelativePath(rel)
    ? path.join(uiRoot, rel.split("/").join(path.sep))
    : null;

  const servePath =
    filePath && fs.existsSync(filePath) && fs.statSync(filePath).isFile()
      ? filePath
      : path.join(uiRoot, "index.html");

  if (!fs.existsSync(servePath)) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.end("Not Found");
    return true;
  }

  const ext = path.extname(servePath).toLowerCase();
  const isHtml = ext === ".html";

  res.setHeader("Content-Type", contentTypeForExt(ext));
  res.setHeader("Cache-Control", "no-cache");

  if (req.method === "HEAD") {
    res.statusCode = 200;
    res.end();
    return true;
  }

  if (isHtml) {
    const raw = fs.readFileSync(servePath, "utf8");
    res.end(injectPandaConfig(raw, opts ?? {}));
  } else {
    res.end(fs.readFileSync(servePath));
  }

  return true;
}
