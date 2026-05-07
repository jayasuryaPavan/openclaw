import "./styles.css";
import { createPandaFace } from "./panda-svg.js";
import { createStt, isSttSupported } from "./stt.js";
import { speak, cancelSpeech } from "./tts.js";
import { sendMessage } from "./chat-client.js";
import { INITIAL_STATE, transition } from "./state.js";
import { EMPTY_HISTORY, appendMessage } from "./history.js";
// ── State ──────────────────────────────────────────────────────────────────
let appState = INITIAL_STATE;
let historyState = EMPTY_HISTORY;
let busy = false;
// ── DOM ────────────────────────────────────────────────────────────────────
const app = document.getElementById("app");
app.innerHTML = `
  <div class="panda-panel">
    <div id="panda-mount"></div>
    <div class="panda-status" id="status-text">Say something…</div>
    <div class="panda-current-msg" id="current-msg"></div>
  </div>
  <div class="chat-panel">
    <div class="chat-header">
      <span class="dot"></span>
      <h1>Panda Chat</h1>
    </div>
    <div class="chat-history" id="chat-history"></div>
    <div class="chat-input-bar">
      <textarea id="text-input" placeholder="Type a message…" rows="1"></textarea>
      <button class="btn btn-mic" id="btn-mic" title="Hold to speak">🎤</button>
      <button class="btn btn-send" id="btn-send" title="Send">➤</button>
    </div>
    <div class="stt-notice" id="stt-notice"></div>
  </div>
`;
const pandaMount = document.getElementById("panda-mount");
const statusEl = document.getElementById("status-text");
const currentMsgEl = document.getElementById("current-msg");
const historyEl = document.getElementById("chat-history");
const textInput = document.getElementById("text-input");
const btnMic = document.getElementById("btn-mic");
const btnSend = document.getElementById("btn-send");
const sttNotice = document.getElementById("stt-notice");
// ── Panda face ─────────────────────────────────────────────────────────────
const panda = createPandaFace();
pandaMount.appendChild(panda.svg);
// ── Render ─────────────────────────────────────────────────────────────────
function render(state) {
    panda.setState(state.panda);
    statusEl.textContent = state.statusText;
    statusEl.dataset["state"] = state.panda;
    currentMsgEl.textContent = state.currentMessage;
    btnSend.disabled = busy;
}
function renderHistory(history) {
    historyEl.innerHTML = "";
    for (const msg of history.messages) {
        const div = document.createElement("div");
        div.className = `msg ${msg.role === "user" ? "user" : "assistant"}`;
        const label = document.createElement("div");
        label.className = "msg-label";
        label.textContent = msg.role === "user" ? "You" : "🐼 Panda";
        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";
        bubble.textContent = msg.text;
        div.append(label, bubble);
        historyEl.appendChild(div);
    }
    historyEl.scrollTop = historyEl.scrollHeight;
}
function showError(msg) {
    const existing = document.querySelector(".error-toast");
    existing?.remove();
    const toast = document.createElement("div");
    toast.className = "error-toast";
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
function update(nextState) {
    appState = nextState;
    render(appState);
}
// ── Send flow ──────────────────────────────────────────────────────────────
async function submitText(text) {
    const trimmed = text.trim();
    if (!trimmed || busy)
        return;
    busy = true;
    historyState = appendMessage(historyState, "user", trimmed);
    renderHistory(historyState);
    textInput.value = "";
    textInput.style.height = "auto";
    update(transition(appState, "thinking", "Thinking…", trimmed));
    try {
        const reply = await sendMessage(trimmed, historyState);
        historyState = appendMessage(historyState, "assistant", reply);
        renderHistory(historyState);
        update(transition(appState, "speaking", "Speaking…", reply));
        speak(reply, {
            onBoundary: () => { },
            onEnd: () => {
                busy = false;
                update(transition(appState, "idle", "Say something…", ""));
            },
        });
    }
    catch (err) {
        busy = false;
        const msg = err instanceof Error ? err.message : String(err);
        showError(`Error: ${msg}`);
        update(transition(appState, "idle", "Something went wrong", ""));
    }
}
// ── Input events ───────────────────────────────────────────────────────────
btnSend.addEventListener("click", () => submitText(textInput.value));
textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitText(textInput.value);
    }
});
textInput.addEventListener("input", () => {
    textInput.style.height = "auto";
    textInput.style.height = `${Math.min(textInput.scrollHeight, 120)}px`;
});
// ── STT ────────────────────────────────────────────────────────────────────
if (!isSttSupported()) {
    btnMic.classList.add("unsupported");
    btnMic.title = "Speech recognition not supported in this browser";
    sttNotice.textContent = "Voice input requires Chrome or Edge";
}
else {
    let sttActive = false;
    let sttFinal = "";
    const stt = createStt({
        onInterim: (text) => {
            textInput.value = sttFinal + text;
        },
        onFinal: (text) => {
            sttFinal += text;
            textInput.value = sttFinal;
        },
        onError: (msg) => {
            sttActive = false;
            btnMic.classList.remove("listening");
            if (msg !== "no-speech")
                showError(`Mic error: ${msg}`);
            update(transition(appState, "idle", "Say something…"));
        },
        onEnd: () => {
            sttActive = false;
            btnMic.classList.remove("listening");
            if (sttFinal.trim()) {
                submitText(sttFinal);
                sttFinal = "";
            }
            else {
                update(transition(appState, "idle", "Say something…"));
            }
        },
    });
    btnMic.addEventListener("click", () => {
        if (busy)
            return;
        if (sttActive) {
            stt.stop();
            return;
        }
        cancelSpeech();
        sttFinal = "";
        textInput.value = "";
        sttActive = true;
        btnMic.classList.add("listening");
        update(transition(appState, "listening", "Listening…", ""));
        stt.start();
    });
}
// ── Init ───────────────────────────────────────────────────────────────────
// Trigger voice list load (Chrome loads voices async)
window.speechSynthesis.getVoices();
window.speechSynthesis.addEventListener("voiceschanged", () => {
    window.speechSynthesis.getVoices();
});
render(appState);
