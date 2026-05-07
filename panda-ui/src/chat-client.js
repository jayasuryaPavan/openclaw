import { toApiMessages } from "./history.js";
function getConfig() {
    const token = window.__PANDA_TOKEN__ ?? "";
    const agentId = window.__PANDA_AGENT_ID__ ?? "panda";
    const baseUrl = window.__PANDA_BASE_URL__ ?? `${location.protocol}//${location.host}`;
    return { token, agentId, baseUrl };
}
export async function sendMessage(userText, history) {
    const { token, agentId, baseUrl } = getConfig();
    const messages = [
        ...toApiMessages(history),
        { role: "user", content: userText },
    ];
    const res = await fetch(`${baseUrl}/v1/chat/completions`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
            model: agentId,
            messages,
            stream: false,
        }),
    });
    if (!res.ok) {
        const body = await res.text().catch(() => "");
        throw new Error(`Gateway error ${res.status}: ${body}`);
    }
    const data = (await res.json());
    const content = data.choices?.[0]?.message?.content;
    if (!content) {
        throw new Error("Empty response from gateway");
    }
    return content;
}
