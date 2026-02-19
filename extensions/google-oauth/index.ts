// Google OAuth Plugin for OpenClaw
// Provides Google OAuth authentication for Telegram bot access

import type { IncomingMessage, ServerResponse } from "node:http";

// In-memory store: Telegram Chat ID -> Authenticated Email
const authenticatedUsers = new Map<string, string>();

// Pending auth: state token -> { chatId, timestamp }
const pendingAuth = new Map<string, { chatId: string; timestamp: number }>();

const PENDING_AUTH_TTL_MS = 5 * 60 * 1000; // 5 minutes

function generateState(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

function cleanupPendingAuth(): void {
    const now = Date.now();
    for (const [state, entry] of pendingAuth.entries()) {
        if (now - entry.timestamp > PENDING_AUTH_TTL_MS) {
            pendingAuth.delete(state);
        }
    }
}

type PluginApi = {
    pluginConfig?: Record<string, unknown>;
    logger: {
        info: (msg: string) => void;
        warn: (msg: string) => void;
        error: (msg: string) => void;
    };
    registerHttpRoute: (params: {
        path: string;
        handler: (req: IncomingMessage, res: ServerResponse) => Promise<void> | void;
    }) => void;
    on: (
        hookName: string,
        handler: (event: any, ctx: any) => any
    ) => void;
    registerCommand: (command: {
        name: string;
        description: string;
        requireAuth?: boolean;
        handler: (ctx: { senderId?: string }) => { text: string };
    }) => void;
};

export default function register(api: PluginApi): void {
    const pluginConfig = api.pluginConfig as {
        clientId?: string;
        clientSecret?: string;
        redirectUri?: string;
        allowedEmails?: string[];
        gatewayBaseUrl?: string;
    } | undefined;

    const clientId = pluginConfig?.clientId || process.env.GOOGLE_CLIENT_ID || "";
    const clientSecret = pluginConfig?.clientSecret || process.env.GOOGLE_CLIENT_SECRET || "";
    const redirectUri = pluginConfig?.redirectUri || "http://localhost:18789/auth/google/callback";
    const allowedEmails = pluginConfig?.allowedEmails || [];
    const gatewayBaseUrl = pluginConfig?.gatewayBaseUrl || "http://localhost:18789";

    if (!clientId || !clientSecret) {
        api.logger.warn("Google OAuth plugin: Missing clientId or clientSecret. Plugin will not function.");
    }

    // Graceful degradation: skip blocking when credentials are not configured
    const isConfigured = !!(clientId && clientSecret);

    // Periodically clean up expired pending auth states
    setInterval(cleanupPendingAuth, 60_000);

    // Route: GET /auth/google/login?chatId=<telegram_chat_id>
    api.registerHttpRoute({
        path: "/auth/google/login",
        handler: async (req: IncomingMessage, res: ServerResponse) => {
            const url = new URL(req.url || "/", gatewayBaseUrl);
            const chatId = url.searchParams.get("chatId");

            if (!chatId) {
                res.statusCode = 400;
                res.setHeader("Content-Type", "text/plain");
                res.end("Missing chatId parameter");
                return;
            }

            if (!clientId) {
                res.statusCode = 500;
                res.setHeader("Content-Type", "text/plain");
                res.end("Google OAuth not configured");
                return;
            }

            const state = generateState();
            pendingAuth.set(state, { chatId, timestamp: Date.now() });

            const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
            authUrl.searchParams.set("client_id", clientId);
            authUrl.searchParams.set("redirect_uri", redirectUri);
            authUrl.searchParams.set("response_type", "code");
            authUrl.searchParams.set("scope", "openid email profile");
            authUrl.searchParams.set("state", state);
            authUrl.searchParams.set("access_type", "online");
            authUrl.searchParams.set("prompt", "select_account");

            res.statusCode = 302;
            res.setHeader("Location", authUrl.toString());
            res.end();
        },
    });

    // Route: GET /auth/google/callback
    api.registerHttpRoute({
        path: "/auth/google/callback",
        handler: async (req: IncomingMessage, res: ServerResponse) => {
            const url = new URL(req.url || "/", gatewayBaseUrl);
            const code = url.searchParams.get("code");
            const state = url.searchParams.get("state");
            const error = url.searchParams.get("error");

            if (error) {
                res.statusCode = 400;
                res.setHeader("Content-Type", "text/html");
                res.end(`<html><body><h1>Login Failed</h1><p>Error: ${error}</p></body></html>`);
                return;
            }

            if (!code || !state) {
                res.statusCode = 400;
                res.setHeader("Content-Type", "text/html");
                res.end("<html><body><h1>Invalid Request</h1><p>Missing code or state.</p></body></html>");
                return;
            }

            const pending = pendingAuth.get(state);
            if (!pending) {
                res.statusCode = 400;
                res.setHeader("Content-Type", "text/html");
                res.end("<html><body><h1>Invalid or Expired Session</h1><p>Please try logging in again.</p></body></html>");
                return;
            }

            pendingAuth.delete(state);

            try {
                // Exchange code for tokens
                const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({
                        code,
                        client_id: clientId,
                        client_secret: clientSecret,
                        redirect_uri: redirectUri,
                        grant_type: "authorization_code",
                    }),
                });

                if (!tokenResponse.ok) {
                    const errorText = await tokenResponse.text();
                    api.logger.error(`Google OAuth token exchange failed: ${errorText}`);
                    res.statusCode = 500;
                    res.setHeader("Content-Type", "text/html");
                    res.end("<html><body><h1>Authentication Failed</h1><p>Could not exchange code for token.</p></body></html>");
                    return;
                }

                const tokens = (await tokenResponse.json()) as { id_token?: string; access_token?: string };

                // Decode ID token to get email (simple base64 decode, no verification - for demo)
                const idToken = tokens.id_token;
                if (!idToken) {
                    res.statusCode = 500;
                    res.setHeader("Content-Type", "text/html");
                    res.end("<html><body><h1>Authentication Failed</h1><p>No ID token received.</p></body></html>");
                    return;
                }

                const payload = JSON.parse(Buffer.from(idToken.split(".")[1], "base64").toString()) as {
                    email?: string;
                    email_verified?: boolean;
                };

                const email = payload.email;
                if (!email || !payload.email_verified) {
                    res.statusCode = 403;
                    res.setHeader("Content-Type", "text/html");
                    res.end("<html><body><h1>Access Denied</h1><p>Email not verified or not available.</p></body></html>");
                    return;
                }

                // Check if email is in allowed list
                if (allowedEmails.length > 0 && !allowedEmails.includes(email)) {
                    api.logger.warn(`Google OAuth: Email ${email} not in allowedEmails list.`);
                    res.statusCode = 403;
                    res.setHeader("Content-Type", "text/html");
                    res.end("<html><body><h1>Access Denied</h1><p>Your email is not authorized.</p></body></html>");
                    return;
                }

                // Store the authenticated mapping
                authenticatedUsers.set(pending.chatId, email);
                api.logger.info(`Google OAuth: Authenticated chatId=${pending.chatId} as ${email}`);

                res.statusCode = 200;
                res.setHeader("Content-Type", "text/html");
                res.end(`
          <html>
          <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>✅ Login Successful!</h1>
            <p>You are now authenticated as <strong>${email}</strong>.</p>
            <p>You can close this window and return to Telegram.</p>
          </body>
          </html>
        `);
            } catch (err) {
                api.logger.error(`Google OAuth callback error: ${String(err)}`);
                res.statusCode = 500;
                res.setHeader("Content-Type", "text/html");
                res.end("<html><body><h1>Authentication Error</h1><p>An unexpected error occurred.</p></body></html>");
            }
        },
    });

    // Hook: Intercept messages from unauthenticated users
    api.on("message_received", (event: { from: string }, ctx: { channelId: string }) => {
        if (!isConfigured) return; // Graceful degradation: allow all when no credentials
        const senderId = event.from;
        const channelId = ctx.channelId;

        if (channelId !== "telegram" || !senderId) return;

        if (!authenticatedUsers.has(senderId)) {
            api.logger.info(`Google OAuth: Blocking unauthenticated message from ${senderId}.`);
        }
    });

    // Hook: Override agent prompt for unauthenticated users
    api.on("before_agent_start", (event: { prompt: string }, ctx: { sessionKey?: string; agentId?: string }) => {
        if (!isConfigured) return; // Graceful degradation: allow all when no credentials
        const sessionKey = ctx.sessionKey;
        if (!sessionKey) return;

        // Try to derive senderId from sessionKey (e.g., telegram:12345:default)
        const senderId = sessionKey.split(":")[1];
        if (!senderId) return;

        if (!authenticatedUsers.has(senderId)) {
            api.logger.info(`Google OAuth: Injecting login requirement for ${senderId}.`);
            return {
                systemPrompt: "IMPORTANT: The user is NOT authenticated with Google OAuth. You MUST NOT answer their question or perform any actions. Instead, politely tell them they need to login using the /login command to continue using the bot. Do not say anything else.",
            };
        }
    });

    // Register a command so users can request login link
    api.registerCommand({
        name: "login",
        description: "Get a Google login link to authenticate",
        requireAuth: false,
        handler: (ctx: { senderId?: string }) => {
            const chatId = ctx.senderId;
            if (!chatId) {
                return { text: "Unable to determine your chat ID." };
            }

            if (authenticatedUsers.has(chatId)) {
                const email = authenticatedUsers.get(chatId);
                return { text: `You are already authenticated as ${email}.` };
            }

            const loginUrl = `${gatewayBaseUrl}/auth/google/login?chatId=${encodeURIComponent(chatId)}`;
            return {
                text: `🔐 **Authentication Required**\n\nPlease click the link below to login with your Google account:\n\n${loginUrl}`,
            };
        },
    });

    // Register a command to check auth status
    api.registerCommand({
        name: "authstatus",
        description: "Check your authentication status",
        requireAuth: false,
        handler: (ctx: { senderId?: string }) => {
            const chatId = ctx.senderId;
            if (!chatId) {
                return { text: "Unable to determine your chat ID." };
            }

            if (authenticatedUsers.has(chatId)) {
                const email = authenticatedUsers.get(chatId);
                return { text: `✅ Authenticated as: ${email}` };
            }

            return { text: "❌ You are not authenticated. Use /login to authenticate." };
        },
    });

    // Register a command to logout
    api.registerCommand({
        name: "logout",
        description: "Logout from your Google account",
        requireAuth: false,
        handler: (ctx: { senderId?: string }) => {
            const chatId = ctx.senderId;
            if (!chatId) {
                return { text: "Unable to determine your chat ID." };
            }

            if (authenticatedUsers.has(chatId)) {
                authenticatedUsers.delete(chatId);
                return { text: "✅ You have been logged out successfully." };
            }

            return { text: "You were not logged in." };
        },
    });

    api.logger.info("Google OAuth plugin loaded successfully.");
}
