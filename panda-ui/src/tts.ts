// Strip [[tts:...]] directives that openclaw injects into agent responses
const TTS_BLOCK_RE = /\[\[tts:[^\]]*\]\]([\s\S]*?)\[\[\/tts:[^\]]*\]\]/g;
const TTS_INLINE_RE = /\[\[tts:[^\]]*\]\]/g;

export function stripTtsDirectives(text: string): string {
  return text.replace(TTS_BLOCK_RE, "$1").replace(TTS_INLINE_RE, "").trim();
}

export interface TtsCallbacks {
  onBoundary: () => void;
  onEnd: () => void;
}

export function speak(rawText: string, callbacks: TtsCallbacks): void {
  const text = stripTtsDirectives(rawText);
  if (!text) {
    callbacks.onEnd();
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  // Prefer a Telugu voice if available, fall back to any English voice
  const voices = window.speechSynthesis.getVoices();
  const teVoice = voices.find((v) => v.lang.startsWith("te"));
  const enVoice = voices.find((v) => v.lang.startsWith("en"));
  if (teVoice) utterance.voice = teVoice;
  else if (enVoice) utterance.voice = enVoice;

  utterance.rate = 1.0;
  utterance.pitch = 1.1;

  utterance.onboundary = () => callbacks.onBoundary();
  utterance.onend = () => callbacks.onEnd();
  utterance.onerror = () => callbacks.onEnd();

  window.speechSynthesis.speak(utterance);
}

export function cancelSpeech(): void {
  window.speechSynthesis.cancel();
}
