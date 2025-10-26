const inputBox = document.querySelector(".input-box");
const sendBtn = document.querySelector(".send-btn");
const chatArea = document.querySelector(".chat-area");
const chatList = document.getElementById("chatList");

let currentChatId = null;
let firstMessage = true;

// Carrega lista de chats ao iniciar
window.addEventListener("load", () => {
  carregarChats();
});

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function appendMessage(user, message) {
  // Se for a primeira mensagem, remove o texto de boas-vindas (se existir)
  if (firstMessage) {
    const welcome = document.querySelector(".welcome-text");
    if (welcome) welcome.remove();
    firstMessage = false;
  }

  const msg = document.createElement("div");
  msg.classList.add("message", user);

  if (user === "bot") {
    msg.innerHTML = marked.parse(message);
  } else {
    msg.textContent = message;
  }

  chatArea.appendChild(msg);
  scrollToBottom();
}

// Salvar o chat
async function baixarChatJSON() {
  if (!currentChatId) return;

  try {
    const res = await fetch(
      `http://localhost:8001/download-json/${currentChatId}`
    );

    if (!res.ok) {
      throw new Error("Erro ao baixar o arquivo JSON");
    }

    // Transforma a resposta em Blob (dados brutos)
    const blob = await res.blob();

    // Cria uma URL temporária para o Blob
    const url = window.URL.createObjectURL(blob);

    // Cria um link invisível para simular o download
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-${currentChatId}.json`; // Nome do arquivo
    document.body.appendChild(a);
    a.click();
    a.remove();

    // Libera a URL da memória
    window.URL.revokeObjectURL(url);

    console.log("Download concluído com sucesso!");
  } catch (err) {
    console.error("Erro ao baixar chat:", err);
  }
}

async function baixarChatCSV() {
  if (!currentChatId) return;

  try {
    const res = await fetch(
      `http://localhost:8001/download-csv/${currentChatId}`
    );

    if (!res.ok) {
      throw new Error("Erro ao baixar o arquivo CSV");
    }

    // Transforma a resposta em Blob (dados brutos)
    const blob = await res.blob();

    // Cria uma URL temporária para o Blob
    const url = window.URL.createObjectURL(blob);

    // Cria um link invisível para simular o download
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-${currentChatId}.csv`; // Nome do arquivo
    document.body.appendChild(a);
    a.click();
    a.remove();

    // Libera a URL da memória
    window.URL.revokeObjectURL(url);

    console.log("Download do CSV concluído com sucesso!");
  } catch (err) {
    console.error("Erro ao baixar chat CSV:", err);
  }
}

function showTyping() {
  const typing = document.createElement("div");
  typing.classList.add("message", "bot", "typing");
  typing.textContent = "Pensando...";
  chatArea.appendChild(typing);
  scrollToBottom();
  return typing;
}

async function criarNovoChat() {
  currentChatId = null;
  firstMessage = true;

  // Limpa a área de chat
  chatArea.innerHTML =
    '<h2 class="welcome-text">No que você está Pensando?</h2>';

  // Remove seleção de todos os chats
  document.querySelectorAll(".chat-item").forEach((item) => {
    item.classList.remove("active");
  });

  // Foca no input
  inputBox.focus();
}

async function carregarChats() {
  try {
    const res = await fetch("http://localhost:8001/chats/");
    const data = await res.json();

    chatList.innerHTML = "";

    if (data.chats && data.chats.length > 0) {
      data.chats.forEach((chat) => {
        adicionarChatNaLista(chat);
      });
    } else {
      chatList.innerHTML =
        '<div style="padding: 15px; text-align: center; color: #9ca3af; font-size: 13px;">Nenhum chat ainda</div>';
    }
  } catch (err) {
    console.error("Erro ao carregar chats:", err);
  }
}

function adicionarChatNaLista(chat) {
  const chatItem = document.createElement("div");
  chatItem.classList.add("chat-item");
  chatItem.dataset.chatId = chat._id;

  const dataFormatada = new Date(chat.atualizado_em).toLocaleDateString(
    "pt-BR",
    {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }
  );

  chatItem.innerHTML = `
          <div class="chat-item-content" onclick="carregarChat('${chat._id}')">
            <div class="chat-item-title">${chat.titulo}</div>
            <div class="chat-item-date">${dataFormatada}</div>
          </div>
          <div class="chat-item-actions">
            <button class="chat-action-btn delete" onclick="deletarChat(event, '${chat._id}')" title="Deletar">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        `;

  chatList.appendChild(chatItem);
}

async function carregarChat(chatId) {
  try {
    const res = await fetch(`http://localhost:8001/chats/${chatId}`);
    const data = await res.json();

    if (data.chat) {
      currentChatId = chatId;
      firstMessage = true;

      // Limpa a área de chat
      chatArea.innerHTML = "";

      // Carrega todas as mensagens
      data.chat.mensagens.forEach((msg) => {
        appendMessage("user", msg.pergunta);
        appendMessage("bot", msg.resposta);
      });

      // Atualiza seleção visual
      document.querySelectorAll(".chat-item").forEach((item) => {
        item.classList.remove("active");
        if (item.dataset.chatId === chatId) {
          item.classList.add("active");
        }
      });

      if (data.chat.mensagens.length === 0) {
        firstMessage = true;
      }
    }
  } catch (err) {
    console.error("Erro ao carregar chat:", err);
  }
}

let chatParaDeletar = null;

function abrirModalConfirmacao(chatId) {
  chatParaDeletar = chatId;
  document.getElementById("confirmModal").style.display = "block";
}

function fecharModal() {
  document.getElementById("confirmModal").style.display = "none";
  chatParaDeletar = null;
}

async function confirmarDelecao() {
  if (!chatParaDeletar) return;

  try {
    const res = await fetch(
      `http://localhost:8001/chats/${chatParaDeletar}/deletar`,
      {
        method: "DELETE",
      }
    );

    if (res.ok) {
      const chatItem = document.querySelector(
        `[data-chat-id="${chatParaDeletar}"]`
      );
      if (chatItem) chatItem.remove();

      if (currentChatId === chatParaDeletar) {
        criarNovoChat();
      }
    } else {
      alert("Erro ao deletar chat");
    }
  } catch (err) {
    console.error("Erro ao deletar chat:", err);
    alert("Erro ao deletar chat");
  } finally {
    fecharModal();
  }
}

async function deletarChat(event, chatId) {
  event.stopPropagation();
  abrirModalConfirmacao(chatId);
}

// Eventos do modal
document.getElementById("cancelarBtn").addEventListener("click", fecharModal);
document
  .getElementById("confirmarBtn")
  .addEventListener("click", confirmarDelecao);

// Fecha se clicar fora
window.addEventListener("click", (event) => {
  const modal = document.getElementById("confirmModal");
  if (event.target === modal) fecharModal();
});

inputBox.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 200) + "px";
  sendBtn.disabled = this.value.trim() === "";
});

sendBtn.addEventListener("click", async function () {
  const message = inputBox.value.trim();
  if (!message) return;

  appendMessage("user", message);
  inputBox.value = "";
  inputBox.style.height = "56px";
  sendBtn.disabled = true;

  // Usar streaming em tempo real
  await enviarMensagemComStreaming(message);
});

// Função para enviar mensagem com streaming
async function enviarMensagemComStreaming(message) {
  let thinkingElement = null;
  let responseElement = null;
  let thinkingText = "";
  let responseText = "";
  let currentEvent = null;

  try {
    // Preparar dados para POST
    const requestBody = JSON.stringify({
      question: message,
      chat_id: currentChatId || "",
      show_thinking: true,
    });

    console.log("[STREAM] Enviando requisição...");

    // Usar fetch com streaming manual (EventSource não suporta POST)
    const response = await fetch("http://localhost:8001/pergunta-stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: requestBody,
    });

    console.log("[STREAM] Resposta recebida, iniciando leitura...");

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log("[STREAM] Leitura concluída");
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;
        
        console.log("[STREAM] Linha recebida:", line);
        
        if (line.startsWith("event:")) {
          currentEvent = line.slice(7).trim();
          console.log("[STREAM] Evento:", currentEvent);
          continue;
        }

        if (line.startsWith("data:")) {
          const data = JSON.parse(line.slice(6));
          console.log("[STREAM] Data:", data, "Evento:", currentEvent);

          // Processar eventos baseado no tipo
          if (currentEvent === "start") {
            console.log("[STREAM] Início do processamento");
          } 
          else if (currentEvent === "thinking_start") {
            console.log("[STREAM] Iniciando thinking");
            if (firstMessage) {
              const welcome = document.querySelector(".welcome-text");
              if (welcome) welcome.remove();
              firstMessage = false;
            }

            thinkingElement = document.createElement("div");
            thinkingElement.classList.add("message", "thinking");
            thinkingElement.innerHTML = '<span class="thinking-label">🤔 Pensando:</span>';
            chatArea.appendChild(thinkingElement);
            scrollToBottom();
          } 
          else if (currentEvent === "thinking" && data.word) {
            console.log("[STREAM] Thinking word:", data.word);
            thinkingText += data.word + " ";
            if (thinkingElement) {
              thinkingElement.innerHTML = `<span class="thinking-label">🤔 Pensando:</span>${thinkingText}<span class="streaming-cursor"></span>`;
              scrollToBottom();
            }
          } 
          else if (currentEvent === "thinking_end") {
            console.log("[STREAM] Thinking finalizado");
            if (thinkingElement) {
              thinkingElement.innerHTML = `<span class="thinking-label">🤔 Pensando:</span>${thinkingText}`;
            }
          } 
          else if (currentEvent === "response_start") {
            console.log("[STREAM] Iniciando resposta");
            responseElement = document.createElement("div");
            responseElement.classList.add("message", "bot", "streaming-message");
            chatArea.appendChild(responseElement);
            scrollToBottom();
          } 
          else if (currentEvent === "response" && data.word) {
            console.log("[STREAM] Response word:", data.word);
            responseText += data.word + " ";
            if (responseElement) {
              responseElement.textContent = responseText;

              const cursor = document.createElement("span");
              cursor.className = "streaming-cursor";
              responseElement.appendChild(cursor);

              scrollToBottom();
            }
          } 
          else if (currentEvent === "complete") {
            console.log("[STREAM] Completo!", data);
            if (responseElement) {
              responseElement.textContent = responseText.trim();
            }

            if (data.chat_id && !currentChatId) {
              currentChatId = data.chat_id;
              carregarChats();
            }

            sendBtn.disabled = false;
            console.log("[STREAM] Concluído!");
          }
          else if (currentEvent === "error") {
            console.error("[STREAM] Erro:", data.message);
            appendMessage("bot", `⚠️ ${data.message}`);
            sendBtn.disabled = false;
          }
        }
      }
    }
  } catch (err) {
    console.error("Erro:", err);
    appendMessage("bot", "⚠️ Erro ao conectar ao servidor.");
    sendBtn.disabled = false;
  }
}

inputBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendBtn.click();
  }
});

// 🪟 Controle do modal
function abrirDownloadModal() {
  if (!currentChatId) return;
  document.getElementById("downloadModal").style.display = "flex";
}

function fecharDownloadModal() {
  document.getElementById("downloadModal").style.display = "none";
}

// Eventos dos botões do modal
document.getElementById("opcaoCSV").addEventListener("click", () => {
  fecharDownloadModal();
  baixarChatCSV();
});

document.getElementById("opcaoJSON").addEventListener("click", () => {
  fecharDownloadModal();
  baixarChatJSON();
});

document
  .getElementById("fecharModal")
  .addEventListener("click", fecharDownloadModal);

// Fecha modal clicando fora
window.addEventListener("click", (e) => {
  const modal = document.getElementById("downloadModal");
  if (e.target === modal) fecharDownloadModal();
});
