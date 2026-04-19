const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chatForm");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("sendBtn");
const sendBtnLabelEl = sendBtn.querySelector("span");
const micBtn = document.getElementById("micBtn");
const micBtnLabelEl = micBtn.querySelector("span");
const clearBtn = document.getElementById("clearBtn");
const clearBtnLabelEl = clearBtn.querySelector("span");
const ptBtn = document.getElementById("ptBtn");
const enBtn = document.getElementById("enBtn");
const assistantTitleEl = document.getElementById("assistantTitle");
const speechStatusEl = document.getElementById("speechStatus");

let idioma = "pt";
let botBubbleCount = 0;

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;
const recognitionSupported = Boolean(recognition);
let isListening = false;
let recognitionBasePrompt = "";

const synthesisSupported = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
const synth = synthesisSupported ? window.speechSynthesis : null;
let voices = [];
const activeSpeech = {
  bubbleId: null,
  text: "",
};

function t(ptText, enText) {
  return idioma === "pt" ? ptText : enText;
}

function setSpeechStatus(text = "") {
  speechStatusEl.textContent = text;
}

function speechLocale() {
  return idioma === "pt" ? "pt-BR" : "en-US";
}

function updateVoiceButtonsState() {
  const allVoiceTools = document.querySelectorAll(".voice-tools");

  allVoiceTools.forEach((tools) => {
    const bubbleId = tools.dataset.bubbleId;
    const toggleBtn = tools.querySelector('[data-action="toggle-speech"]');
    const repeatBtn = tools.querySelector('[data-action="repeat-speech"]');
    const toggleLabel = toggleBtn?.querySelector("span");
    const repeatLabel = repeatBtn?.querySelector("span");

    if (repeatLabel) {
      repeatLabel.textContent = t("Repetir", "Repeat");
    }

    if (!toggleBtn || !toggleLabel) return;

    const isCurrentBubble = activeSpeech.bubbleId === bubbleId;
    if (isCurrentBubble && synth?.speaking && !synth.paused) {
      toggleBtn.classList.add("active");
      toggleLabel.textContent = t("Pausar", "Pause");
      return;
    }

    if (isCurrentBubble && synth?.paused) {
      toggleBtn.classList.add("active");
      toggleLabel.textContent = t("Continuar", "Resume");
      return;
    }

    toggleBtn.classList.remove("active");
    toggleLabel.textContent = t("Ouvir", "Play");
  });
}

function updateRecognitionLanguage() {
  if (!recognition) return;
  recognition.lang = speechLocale();
}

function updateMicButtonState() {
  micBtn.classList.toggle("listening", isListening);
  micBtn.setAttribute("aria-pressed", String(isListening));
}

function chooseBestVoice(locale) {
  if (!voices.length) return null;
  const lowerLocale = locale.toLowerCase();
  const langPrefix = lowerLocale.split("-")[0];

  const ranked = voices
    .filter((voice) => voice.lang?.toLowerCase().startsWith(langPrefix))
    .map((voice) => {
      const name = voice.name.toLowerCase();
      let score = 0;
      if (voice.lang.toLowerCase() === lowerLocale) score += 4;
      if (name.includes("google")) score += 3;
      if (name.includes("microsoft")) score += 2;
      if (name.includes("natural") || name.includes("neural")) score += 2;
      if (voice.default) score += 1;
      return { voice, score };
    })
    .sort((a, b) => b.score - a.score);

  return ranked[0]?.voice || null;
}

function stopCurrentSpeech() {
  if (!synthesisSupported) return;
  synth.cancel();
  activeSpeech.bubbleId = null;
  activeSpeech.text = "";
  updateVoiceButtonsState();
}

function speakForBubble(bubbleId, text, { restart = false } = {}) {
  if (!synthesisSupported || !text.trim()) return;

  const sameBubble = activeSpeech.bubbleId === bubbleId;
  if (sameBubble && synth.speaking && !restart) {
    if (synth.paused) {
      synth.resume();
      setSpeechStatus(t("Audio retomado.", "Audio resumed."));
    } else {
      synth.pause();
      setSpeechStatus(t("Audio pausado.", "Audio paused."));
    }
    updateVoiceButtonsState();
    return;
  }

  stopCurrentSpeech();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = speechLocale();
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.volume = 1;

  const selectedVoice = chooseBestVoice(utterance.lang);
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  activeSpeech.bubbleId = bubbleId;
  activeSpeech.text = text;

  utterance.onstart = () => {
    setSpeechStatus(t("Lendo resposta em voz alta...", "Reading response out loud..."));
    updateVoiceButtonsState();
  };

  utterance.onend = () => {
    if (activeSpeech.bubbleId === bubbleId) {
      activeSpeech.bubbleId = null;
      activeSpeech.text = "";
    }
    setSpeechStatus("");
    updateVoiceButtonsState();
  };

  utterance.onerror = () => {
    if (activeSpeech.bubbleId === bubbleId) {
      activeSpeech.bubbleId = null;
      activeSpeech.text = "";
    }
    setSpeechStatus(t("Nao foi possivel reproduzir o audio.", "Could not play audio."));
    updateVoiceButtonsState();
  };

  synth.speak(utterance);
}

function createVoiceTools(bubbleId, text) {
  const footer = document.createElement("footer");
  footer.className = "bubble-footer";

  const tools = document.createElement("div");
  tools.className = "voice-tools";
  tools.dataset.bubbleId = bubbleId;

  const playPauseBtn = document.createElement("button");
  playPauseBtn.className = "voice-btn";
  playPauseBtn.type = "button";
  playPauseBtn.dataset.action = "toggle-speech";
  playPauseBtn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M8 6V18L18 12L8 6Z"></path>
    </svg>
    <span>${t("Ouvir", "Play")}</span>
  `;

  const repeatBtn = document.createElement("button");
  repeatBtn.className = "voice-btn";
  repeatBtn.type = "button";
  repeatBtn.dataset.action = "repeat-speech";
  repeatBtn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M20 10V4L14 4"></path>
      <path d="M4 14V20H10"></path>
      <path d="M20 4L13 11"></path>
      <path d="M4 20L11 13"></path>
    </svg>
    <span>${t("Repetir", "Repeat")}</span>
  `;

  if (!synthesisSupported) {
    playPauseBtn.disabled = true;
    repeatBtn.disabled = true;
    playPauseBtn.title = t("Audio nao suportado neste navegador.", "Audio is not supported in this browser.");
    repeatBtn.title = playPauseBtn.title;
  }

  playPauseBtn.addEventListener("click", () => speakForBubble(bubbleId, text, { restart: false }));
  repeatBtn.addEventListener("click", () => speakForBubble(bubbleId, text, { restart: true }));

  tools.append(playPauseBtn, repeatBtn);
  footer.appendChild(tools);
  return footer;
}

function setLanguage(nextLang) {
  idioma = nextLang;
  ptBtn.classList.toggle("active", nextLang === "pt");
  enBtn.classList.toggle("active", nextLang === "en");
  promptEl.placeholder =
    nextLang === "pt" ? "Digite sua pergunta..." : "Type your question...";
  if (assistantTitleEl) assistantTitleEl.textContent = t("Assistente Inteligente", "Smart Assistant");
  if (sendBtnLabelEl) sendBtnLabelEl.textContent = t("Enviar", "Send");
  if (micBtnLabelEl) micBtnLabelEl.textContent = t("Voz", "Voice");
  if (clearBtnLabelEl) clearBtnLabelEl.textContent = t("Limpar", "Clear");
  updateRecognitionLanguage();
  updateVoiceButtonsState();
}

function appendBubble(role, text, options = {}) {
  const { autoSpeak = false } = options;
  const bubble = document.createElement("article");
  bubble.className = `bubble ${role}`;

  const meta = document.createElement("span");
  meta.className = "meta";
  meta.textContent = role === "user" ? (idioma === "pt" ? "Voce" : "You") : "Pity-IA";
  bubble.appendChild(meta);

  const content = document.createElement("div");
  content.className = "bubble-content";
  content.textContent = text;
  bubble.appendChild(content);

  let bubbleId = null;
  if (role === "bot") {
    botBubbleCount += 1;
    bubbleId = `bot-${Date.now()}-${botBubbleCount}`;
    bubble.dataset.bubbleId = bubbleId;
    bubble.appendChild(createVoiceTools(bubbleId, text));
  }

  chatEl.appendChild(bubble);
  chatEl.scrollTop = chatEl.scrollHeight;

  if (role === "bot" && autoSpeak && bubbleId) {
    speakForBubble(bubbleId, text, { restart: true });
  }
}

async function askBot(prompt) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, idioma }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const data = await response.json();
  return data?.texto || "Sem resposta.";
}

function setupSpeechRecognition() {
  if (!recognition) {
    micBtn.disabled = true;
    setSpeechStatus(t("Reconhecimento de voz nao suportado neste navegador.", "Voice recognition is not supported in this browser."));
    return;
  }

  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.maxAlternatives = 1;
  updateRecognitionLanguage();

  recognition.onstart = () => {
    isListening = true;
    updateMicButtonState();
    setSpeechStatus(t("Ouvindo... fale agora.", "Listening... speak now."));
  };

  recognition.onresult = (event) => {
    let transcript = "";
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      transcript += event.results[i][0].transcript;
    }

    const normalized = transcript.trim();
    if (!normalized) return;
    promptEl.value = recognitionBasePrompt
      ? `${recognitionBasePrompt} ${normalized}`.trim()
      : normalized;
    promptEl.focus();
  };

  recognition.onerror = (event) => {
    const err = event?.error || "unknown";
    if (err === "not-allowed") {
      setSpeechStatus(t("Permissao de microfone negada.", "Microphone permission denied."));
    } else if (err === "no-speech") {
      setSpeechStatus(t("Nenhuma fala detectada.", "No speech detected."));
    } else {
      setSpeechStatus(t("Falha ao capturar voz.", "Failed to capture voice."));
    }
  };

  recognition.onend = () => {
    isListening = false;
    updateMicButtonState();
    if (promptEl.value.trim()) {
      setSpeechStatus(t("Transcricao pronta.", "Transcription ready."));
    }
  };
}

function toggleListening() {
  if (!recognition) return;

  if (isListening) {
    recognition.stop();
    setSpeechStatus(t("Captura de voz finalizada.", "Voice capture stopped."));
    return;
  }

  recognitionBasePrompt = promptEl.value.trim();
  try {
    recognition.start();
  } catch {
    setSpeechStatus(t("Nao foi possivel iniciar o microfone.", "Could not start microphone."));
  }
}

function loadVoices() {
  if (!synthesisSupported) return;
  voices = synth.getVoices();
}

function clearConversation() {
  const shouldClear = window.confirm(
    t(
      "Tem certeza que deseja limpar a conversa? Esta acao nao pode ser desfeita.",
      "Are you sure you want to clear the conversation? This action cannot be undone."
    )
  );

  if (!shouldClear) {
    setSpeechStatus(t("Limpeza cancelada.", "Clear action canceled."));
    return;
  }

  if (isListening && recognition) {
    recognition.stop();
  }

  stopCurrentSpeech();
  chatEl.innerHTML = "";
  botBubbleCount = 0;
  promptEl.value = "";
  promptEl.focus();
  setSpeechStatus(t("Conversa limpa. Pronto para uma nova pergunta.", "Chat cleared. Ready for a new question."));
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  if (isListening && recognition) {
    recognition.stop();
  }

  appendBubble("user", prompt);
  promptEl.value = "";
  sendBtn.disabled = true;
  micBtn.disabled = true;

  try {
    const botText = await askBot(prompt);
    appendBubble("bot", botText, { autoSpeak: true });
  } catch (error) {
    appendBubble("bot", `Erro: ${error.message}`, { autoSpeak: false });
  } finally {
    sendBtn.disabled = false;
    micBtn.disabled = !recognitionSupported;
    promptEl.focus();
  }
});

ptBtn.addEventListener("click", () => setLanguage("pt"));
enBtn.addEventListener("click", () => setLanguage("en"));
micBtn.addEventListener("click", toggleListening);
clearBtn.addEventListener("click", clearConversation);

appendBubble(
  "bot",
  "Ola. Sou a Pity-IA. Posso conversar por texto e tambem responder em audio."
);

setupSpeechRecognition();
if (synthesisSupported) {
  loadVoices();
  window.speechSynthesis.onvoiceschanged = loadVoices;
} else {
  setSpeechStatus(t("Sintese de voz nao suportada neste navegador.", "Speech synthesis is not supported in this browser."));
}
updateMicButtonState();
updateVoiceButtonsState();
