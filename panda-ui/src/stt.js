export function isSttSupported() {
    return !!(window.SpeechRecognition ?? window.webkitSpeechRecognition);
}
export function createStt(callbacks) {
    const Ctor = window.SpeechRecognition ?? window.webkitSpeechRecognition;
    if (!Ctor) {
        throw new Error("SpeechRecognition not supported in this browser");
    }
    const recognition = new Ctor();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onresult = (e) => {
        let interim = "";
        let final = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
            const result = e.results[i];
            if (!result)
                continue;
            const transcript = result[0]?.transcript ?? "";
            if (result.isFinal) {
                final += transcript;
            }
            else {
                interim += transcript;
            }
        }
        if (interim)
            callbacks.onInterim(interim);
        if (final)
            callbacks.onFinal(final);
    };
    recognition.onerror = (e) => {
        callbacks.onError(e.error ?? "unknown STT error");
    };
    recognition.onend = () => {
        callbacks.onEnd();
    };
    return {
        start: () => recognition.start(),
        stop: () => recognition.stop(),
    };
}
