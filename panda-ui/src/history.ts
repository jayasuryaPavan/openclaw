const MAX_HISTORY = 20;

export type Role = "user" | "assistant";

export interface ChatMessage {
  readonly role: Role;
  readonly text: string;
  readonly id: number;
}

export interface HistoryState {
  readonly messages: readonly ChatMessage[];
  readonly nextId: number;
}

export const EMPTY_HISTORY: HistoryState = { messages: [], nextId: 1 };

export function appendMessage(history: HistoryState, role: Role, text: string): HistoryState {
  const message: ChatMessage = { role, text, id: history.nextId };
  const messages = [...history.messages, message].slice(-MAX_HISTORY);
  return { messages, nextId: history.nextId + 1 };
}

export function toApiMessages(history: HistoryState): Array<{ role: string; content: string }> {
  return history.messages.map((m) => ({ role: m.role, content: m.text }));
}
