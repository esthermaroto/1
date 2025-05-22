// Variables de configuración
const API_URL = 'http://localhost:8080'; // URL de la API (puerto 8080)

// Elementos del DOM
const chatHistory = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Historial de la conversación - No usado actualmente por el backend simple
// const conversationHistory = [];

// Emojis divertidos para usar como avatares de usuario
// const userEmojis = ["😎", "🤩", "🦸", "🧙", "🥳", "🦊", "🐱", "🐼", "🐯", "🦁", "🐶", "🦄", "🐲", "🐸", "🐵"];

// Función para obtener un emoji aleatorio
// function getRandomUserEmoji() {
//     return userEmojis[Math.floor(Math.random() * userEmojis.length)];
// }

// Guarda el emoji seleccionado para este usuario
// const userEmoji = getRandomUserEmoji();

// Eliminar elementos de modo si existen - Ya no son relevantes para el backend simple
const oldModeSelector = document.getElementById('modeSelector');
if (oldModeSelector) oldModeSelector.remove();

// Eliminar la lógica de los botones de modo si existen
// const chatInputArea = document.querySelector('.chat-input-area');
// if (chatInputArea) {
//     const modeSelector = document.getElementById('modeSelector');
//     if (modeSelector) modeSelector.remove();
// }

// let currentMode = 'github'; // Ya no es relevante

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    if (isUser) {
        avatar.innerHTML = '<i class="fas fa-user"></i>'; // Icono genérico de usuario
        avatar.setAttribute('title', 'Tú');
    } else {
        // Usar la imagen del robot para el avatar del bot
        avatar.innerHTML = '<img src="/static/img/robot.png" alt="Robot Avatar" class="chat-bot-avatar">';
        avatar.setAttribute('title', 'Asistente');
    }

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    // Convertir markdown a HTML si no es un mensaje del usuario
    if (!isUser && typeof marked !== 'undefined') {
        bubble.innerHTML = marked.parse(text);
    } else {
        bubble.textContent = text;
    }
    
    // Ordenar avatar y burbuja
    if (isUser) {
        messageDiv.appendChild(bubble);
        messageDiv.appendChild(avatar);
        messageDiv.style.justifyContent = 'flex-end'; // Alinear a la derecha para usuario
    } else {
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        messageDiv.style.justifyContent = 'flex-start'; // Alinear a la izquierda para bot
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    // Animación simple de aparición
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease-out';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);

    // No guardar en el historial por ahora, el backend no lo usa
    // conversationHistory.push({ role: isUser ? 'user' : 'assistant', content: text });
}

// Función para mostrar el indicador de escritura
function showTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message bot-message typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    // Usar la imagen del robot para el avatar del indicador
    avatar.innerHTML = '<img src="/static/img/robot.png" alt="Robot Avatar" class="chat-bot-avatar">';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = '<span></span><span></span><span></span>'; // Indicador animado

    indicatorDiv.appendChild(avatar);
    indicatorDiv.appendChild(bubble);
    chatHistory.appendChild(indicatorDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return indicatorDiv;
}

// Función para enviar mensaje y recibir respuesta del backend
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Añadir mensaje del usuario
    addMessage(message, true);
    chatInput.value = '';
    chatInput.style.height = 'auto'; // Reset height

    // Mostrar indicador de escritura
    const typingIndicator = showTypingIndicator();

    try {
        // Realizar la petición POST al backend
        const response = await fetch(`${API_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        // Eliminar indicador de escritura antes de procesar la respuesta
        typingIndicator.remove();

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error del servidor: ${response.status}`);
        }

        const data = await response.json();
        
        // Añadir respuesta del bot
        if (data.response) {
            addMessage(data.response, false);
        } else {
            addMessage('Lo siento, no pude obtener una respuesta válida del servidor.', false);
            console.error('Respuesta inesperada del servidor:', data);
        }

    } catch (error) {
        console.error('Error al enviar mensaje o recibir respuesta:', error);
        if (typingIndicator && typingIndicator.parentNode) {
            typingIndicator.remove();
        }
        addMessage(`Lo siento, ha ocurrido un error: ${error.message}`, false);
    }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
    
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-ajustar la altura del textarea
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    const newHeight = Math.min(chatInput.scrollHeight, 120); // Limitar altura máxima a 120px
    chatInput.style.height = newHeight + 'px';
});

// Ajustar altura inicial del textarea
window.addEventListener('load', () => {
     chatInput.style.height = 'auto';
     chatInput.style.height = (chatInput.scrollHeight) + 'px';
});

// Mensaje de bienvenida al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    // Pequeño retraso para la animación
    setTimeout(() => {
        addMessage('¡Hola! Soy el asistente de FicZone. ¿En qué puedo ayudarte hoy?', false);
    }, 300);
});
