const MAX_HISTORY = 20;
export const EMPTY_HISTORY = { messages: [], nextId: 1 };
export function appendMessage(history, role, text) {
    const message = { role, text, id: history.nextId };
    const messages = [...history.messages, message].slice(-MAX_HISTORY);
    return { messages, nextId: history.nextId + 1 };
}
export function toApiMessages(history) {
    return history.messages.map((m) => ({ role: m.role, content: m.text }));
}
