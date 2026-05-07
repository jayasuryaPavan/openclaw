export function transition(state, panda, statusText, currentMessage) {
    return { ...state, panda, statusText, currentMessage: currentMessage ?? state.currentMessage };
}
export const INITIAL_STATE = {
    panda: "idle",
    statusText: "Say something…",
    currentMessage: "",
};
