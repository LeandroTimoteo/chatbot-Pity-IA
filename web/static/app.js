const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chatForm");
const promptEl = document.getElementById("prompt");
const sendBtn = document.getElementById("sendBtn");
const ptBtn = document.getElementById("ptBtn");
const enBtn = document.getElementById("enBtn");

let idioma = "pt";

function setLanguage(nextLang) {
  idioma = nextLang;
  ptBtn.classList.toggle("active", nextLang === "pt");
  enBtn.classList.toggle("active", nextLang === "en");
  promptEl.placeholder =
    nextLang === "pt" ? "Digite sua pergunta..." : "Type your question...";
  sendBtn.textContent = nextLang === "pt" ? "Enviar" : "Send";
}

function appendBubble(role, text) {
  const bubble = document.createElement("article");
  bubble.className = `bubble ${role}`;

  const meta = document.createElement("span");
  meta.className = "meta";
  meta.textContent = role === "user" ? (idioma === "pt" ? "Voce" : "You") : "Pity-IA";
  bubble.appendChild(meta);

  const content = document.createElement("div");
  content.textContent = text;
  bubble.appendChild(content);

  chatEl.appendChild(bubble);
  chatEl.scrollTop = chatEl.scrollHeight;
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

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;

  appendBubble("user", prompt);
  promptEl.value = "";
  sendBtn.disabled = true;

  try {
    const botText = await askBot(prompt);
    appendBubble("bot", botText);
  } catch (error) {
    appendBubble("bot", `Erro: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    promptEl.focus();
  }
});

ptBtn.addEventListener("click", () => setLanguage("pt"));
enBtn.addEventListener("click", () => setLanguage("en"));

appendBubble(
  "bot",
  "Pity-IA web carregada. Escreva sua mensagem para testar sem os avisos de feature policy do Streamlit."
);

