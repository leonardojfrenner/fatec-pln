// Configuração da API
const API_URL = 'http://localhost:8000';

// Elementos do DOM
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const showThinkingCheckbox = document.getElementById('showThinking');
const maxTokensInput = document.getElementById('maxTokens');

// Estado
let isLoading = false;

// Event Listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
});

// Função para enviar mensagem com streaming
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) {
        return;
    }

    // Limpar welcome message se existir
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    // Adicionar mensagem do usuário
    addUserMessage(message);

    // Limpar input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Desabilitar botão
    setLoading(true);

    // Criar elementos para streaming
    const streamElements = createStreamingMessage();
    
    try {
        // Fazer requisição com streaming
        const response = await fetch(`${API_URL}/pergunta-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: message,
                max_tokens: parseInt(maxTokensInput.value)
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao processar pergunta');
        }

        // Processar stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { value, done } = await reader.read();
            
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6);
                    
                    try {
                        // Usar eval para processar a string Python-like
                        const data = eval('(' + dataStr + ')');
                        
                        if (data.type === 'thinking_chunk') {
                            updateStreamingThinking(streamElements.thinking, data.content);
                        } else if (data.type === 'thinking') {
                            updateStreamingThinking(streamElements.thinking, data.content);
                        } else if (data.type === 'response_chunk') {
                            updateStreamingResponse(streamElements.response, data.content);
                        } else if (data.type === 'response') {
                            updateStreamingResponse(streamElements.response, data.content);
                        } else if (data.type === 'done') {
                            // Finalizado - remover cursores
                            if (streamElements.thinking) {
                                const cursor = streamElements.thinking.querySelector('.streaming-cursor');
                                if (cursor) cursor.remove();
                            }
                            if (streamElements.response) {
                                const cursor = streamElements.response.querySelector('.streaming-cursor');
                                if (cursor) cursor.remove();
                            }
                            console.log('Streaming concluído');
                        }
                    } catch (e) {
                        console.warn('Erro ao parsear chunk:', e);
                    }
                }
            }
        }

    } catch (error) {
        // Remover elementos de streaming
        if (streamElements.container.parentNode) {
            streamElements.container.remove();
        }

        // Mostrar erro
        addErrorMessage(error.message);
        
        console.error('Erro:', error);
    } finally {
        setLoading(false);
    }
}

// Criar elementos para streaming
function createStreamingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    
    const wrapper = document.createElement('div');
    wrapper.style.maxWidth = '80%';

    let thinkingDiv = null;
    let thinkingText = null;

    // Criar thinking se habilitado
    if (showThinkingCheckbox.checked) {
        thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'thinking-content';
        
        const label = document.createElement('div');
        label.className = 'thinking-label';
        label.innerHTML = '🧠 Pensamento do modelo:';
        
        thinkingText = document.createElement('div');
        thinkingText.textContent = '';
        
        thinkingDiv.appendChild(label);
        thinkingDiv.appendChild(thinkingText);
        wrapper.appendChild(thinkingDiv);
    }

    // Criar elemento de resposta
    const responseDiv = document.createElement('div');
    responseDiv.className = 'message-content';
    responseDiv.textContent = '';
    
    wrapper.appendChild(responseDiv);
    messageDiv.appendChild(wrapper);
    chatContainer.appendChild(messageDiv);
    
    scrollToBottom();

    return {
        container: messageDiv,
        thinking: thinkingText,
        response: responseDiv
    };
}

// Atualizar pensamento em streaming
function updateStreamingThinking(thinkingElement, content) {
    if (thinkingElement && showThinkingCheckbox.checked) {
        // Remover cursor se existir
        const cursor = thinkingElement.querySelector('.streaming-cursor');
        if (cursor) cursor.remove();
        
        thinkingElement.textContent += content;
        
        // Adicionar cursor piscando
        const newCursor = document.createElement('span');
        newCursor.className = 'streaming-cursor';
        thinkingElement.appendChild(newCursor);
        
        scrollToBottom();
    }
}

// Atualizar resposta em streaming
function updateStreamingResponse(responseElement, content) {
    if (responseElement) {
        // Remover cursor se existir
        const cursor = responseElement.querySelector('.streaming-cursor');
        if (cursor) cursor.remove();
        
        responseElement.textContent += content;
        
        // Adicionar cursor piscando
        const newCursor = document.createElement('span');
        newCursor.className = 'streaming-cursor';
        responseElement.appendChild(newCursor);
        
        scrollToBottom();
    }
}

// Adicionar mensagem do usuário
function addUserMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-user';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    scrollToBottom();
}

// Adicionar loading
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = `
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    `;
    
    messageDiv.appendChild(loadingDiv);
    chatContainer.appendChild(messageDiv);
    
    scrollToBottom();
    
    return messageDiv;
}

// Adicionar mensagem de erro
function addErrorMessage(errorText) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<strong>❌ Erro:</strong> ${errorText}`;
    
    chatContainer.appendChild(errorDiv);
    
    scrollToBottom();
}

// Controlar estado de loading
function setLoading(loading) {
    isLoading = loading;
    sendButton.disabled = loading;
    messageInput.disabled = loading;
}

// Scroll para o final
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Verificar se a API está disponível ao carregar
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_URL}/saude`);
        if (response.ok) {
            console.log('✅ API conectada com sucesso!');
        }
    } catch (error) {
        console.warn('⚠️ Não foi possível conectar à API. Verifique se está rodando em:', API_URL);
        addErrorMessage('Não foi possível conectar à API. Certifique-se de que está rodando em ' + API_URL);
    }
});

