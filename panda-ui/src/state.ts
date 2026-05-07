export type PandaState = "idle" | "listening" | "thinking" | "speaking";

export interface AppState {
  readonly panda: PandaState;
  readonly statusText: string;
  readonly currentMessage: string;
}

export function transition(state: AppState, panda: PandaState, statusText: string, currentMessage?: string): AppState {
  return { ...state, panda, statusText, currentMessage: currentMessage ?? state.currentMessage };
}

export const INITIAL_STATE: AppState = {
  panda: "idle",
  statusText: "Say something…",
  currentMessage: "",
};
