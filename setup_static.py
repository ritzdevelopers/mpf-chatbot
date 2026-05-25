#!/usr/bin/env python
"""Setup script to create static files for the chatbot UI"""
import os
import json

# Create static folder
os.makedirs("static", exist_ok=True)

# HTML File
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chatbot Assistant</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- AI Background Animation -->
    <div class="background-container">
        <div class="gradient-bg"></div>
        <div class="floating-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
            <div class="shape shape-4"></div>
        </div>
        <div class="network-animation">
            <svg class="network-svg" viewBox="0 0 1200 600">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <circle cx="100" cy="100" r="8" class="node" filter="url(#glow)"/>
                <circle cx="1100" cy="100" r="8" class="node" filter="url(#glow)"/>
                <circle cx="600" cy="500" r="8" class="node" filter="url(#glow)"/>
                <circle cx="300" cy="400" r="6" class="node" filter="url(#glow)"/>
                <circle cx="900" cy="400" r="6" class="node" filter="url(#glow)"/>
                
                <line x1="100" y1="100" x2="1100" y2="100" class="connection" stroke-dasharray="2000" stroke-dashoffset="2000"/>
                <line x1="100" y1="100" x2="600" y2="500" class="connection" stroke-dasharray="2000" stroke-dashoffset="2000"/>
                <line x1="1100" y1="100" x2="600" y2="500" class="connection" stroke-dasharray="2000" stroke-dashoffset="2000"/>
                <line x1="300" y1="400" x2="900" y2="400" class="connection" stroke-dasharray="2000" stroke-dashoffset="2000"/>
            </svg>
        </div>
    </div>

    <!-- Floating Chatbot Button -->
    <button class="chatbot-toggle" id="chatbotToggle" title="Open Chat">
        <div class="chat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
        </div>
        <span class="pulse"></span>
    </button>

    <!-- Chatbot Modal -->
    <div class="chatbot-modal" id="chatbotModal">
        <div class="chatbot-container">
            <!-- Header -->
            <div class="chatbot-header">
                <div class="header-content">
                    <div class="bot-avatar">
                        <div class="avatar-glow"></div>
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <circle cx="12" cy="12" r="10"/>
                            <circle cx="9" cy="11" r="1.5" fill="white"/>
                            <circle cx="15" cy="11" r="1.5" fill="white"/>
                            <path d="M9 15a3 3 0 0 0 6 0" stroke="white" stroke-width="2" fill="none"/>
                        </svg>
                    </div>
                    <div>
                        <h2>AI Assistant</h2>
                        <p class="status"><span class="status-dot"></span>Online</p>
                    </div>
                </div>
                <button class="close-btn" id="closeChat">✕</button>
            </div>

            <!-- Messages Area -->
            <div class="chatbot-messages" id="messagesContainer">
                <div class="message bot-message welcome-message">
                    <div class="message-avatar">
                        <svg viewBox="0 0 24 24" fill="currentColor">
                            <circle cx="12" cy="12" r="10"/>
                        </svg>
                    </div>
                    <div class="message-content">
                        <p>👋 Hello! I'm your AI Assistant. How can I help you today? Ask me anything about real estate or any other questions!</p>
                    </div>
                </div>
            </div>

            <!-- Input Area -->
            <div class="chatbot-input-area">
                <form class="input-form" id="chatForm">
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Type your message..." 
                        class="message-input"
                        autocomplete="off"
                    >
                    <button type="submit" class="send-btn" id="sendBtn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </form>
                <div class="typing-indicator hidden" id="typingIndicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    </div>

    <!-- Overlay -->
    <div class="modal-overlay hidden" id="modalOverlay"></div>

    <script src="script.js"></script>
</body>
</html>'''

# CSS File
css_content = '''/* ============================
   VARIABLES
   ============================ */
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --accent-color: #ec4899;
    --bg-color: #0f172a;
    --surface-color: #1e293b;
    --surface-light: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --border-color: #475569;
    --success-color: #10b981;
    --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --gradient-2: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
}

/* ============================
   GLOBAL STYLES
   ============================ */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-primary);
    overflow: hidden;
    height: 100vh;
}

/* ============================
   BACKGROUND CONTAINER
   ============================ */
.background-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    overflow: hidden;
}

.gradient-bg {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        135deg,
        rgba(99, 102, 241, 0.1) 0%,
        rgba(139, 92, 246, 0.05) 25%,
        rgba(236, 72, 153, 0.08) 50%,
        rgba(15, 23, 42, 1) 100%
    );
}

/* ============================
   FLOATING SHAPES
   ============================ */
.floating-shapes {
    position: absolute;
    width: 100%;
    height: 100%;
}

.shape {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    filter: blur(40px);
}

.shape-1 {
    width: 300px;
    height: 300px;
    background: var(--primary-color);
    top: 10%;
    left: 10%;
    animation: float 15s infinite ease-in-out;
}

.shape-2 {
    width: 200px;
    height: 200px;
    background: var(--secondary-color);
    bottom: 10%;
    right: 10%;
    animation: float 20s infinite ease-in-out reverse;
}

.shape-3 {
    width: 250px;
    height: 250px;
    background: var(--accent-color);
    top: 50%;
    right: 5%;
    animation: float 18s infinite ease-in-out;
}

.shape-4 {
    width: 150px;
    height: 150px;
    background: var(--primary-color);
    bottom: 20%;
    left: 15%;
    animation: float 22s infinite ease-in-out reverse;
}

@keyframes float {
    0%, 100% {
        transform: translateY(0px) translateX(0px);
    }
    25% {
        transform: translateY(-20px) translateX(10px);
    }
    50% {
        transform: translateY(-40px) translateX(-10px);
    }
    75% {
        transform: translateY(-20px) translateX(10px);
    }
}

/* ============================
   NETWORK ANIMATION
   ============================ */
.network-animation {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
}

.network-svg {
    width: 100%;
    height: 100%;
    opacity: 0.15;
}

.node {
    fill: var(--primary-color);
    animation: pulse-node 2s infinite;
}

.connection {
    stroke: var(--secondary-color);
    stroke-width: 1;
    animation: draw-line 3s infinite;
}

@keyframes pulse-node {
    0%, 100% {
        r: 8;
        opacity: 0.6;
    }
    50% {
        r: 12;
        opacity: 0.3;
    }
}

@keyframes draw-line {
    0% {
        stroke-dashoffset: 2000;
    }
    50% {
        stroke-dashoffset: 0;
    }
    100% {
        stroke-dashoffset: -2000;
    }
}

/* ============================
   FLOATING BUTTON
   ============================ */
.chatbot-toggle {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--gradient-1);
    border: none;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    z-index: 1000;
    transition: all 0.3s ease;
    font-size: 24px;
}

.chatbot-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 12px 32px rgba(99, 102, 241, 0.6);
}

.chatbot-toggle:active {
    transform: scale(0.95);
}

.chat-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

.chat-icon svg {
    width: 28px;
    height: 28px;
    stroke: currentColor;
}

.pulse {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: var(--gradient-1);
    animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
    0% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
    }
    50% {
        box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
    }
}

/* ============================
   MODAL OVERLAY
   ============================ */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 999;
    opacity: 1;
    transition: opacity 0.3s ease;
}

.modal-overlay.hidden {
    display: none;
    opacity: 0;
}

/* ============================
   CHATBOT MODAL
   ============================ */
.chatbot-modal {
    position: fixed;
    bottom: 100px;
    right: 24px;
    width: 400px;
    height: 600px;
    background: var(--surface-color);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    z-index: 1001;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid var(--border-color);
    animation: slide-up 0.3s ease;
}

.chatbot-modal.hidden {
    display: none;
    animation: slide-down 0.3s ease;
}

@keyframes slide-up {
    from {
        transform: translateY(20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes slide-down {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(20px);
        opacity: 0;
    }
}

.chatbot-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--surface-color);
}

/* ============================
   CHATBOT HEADER
   ============================ */
.chatbot-header {
    padding: 20px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
}

.bot-avatar {
    position: relative;
    width: 44px;
    height: 44px;
}

.avatar-glow {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--gradient-1);
    border-radius: 50%;
    animation: avatar-glow 2s infinite;
    opacity: 0.5;
}

.bot-avatar svg {
    position: relative;
    width: 100%;
    height: 100%;
    color: var(--primary-color);
    z-index: 1;
}

@keyframes avatar-glow {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
    }
    50% {
        box-shadow: 0 0 0 8px rgba(99, 102, 241, 0);
    }
}

.header-content h2 {
    font-size: 16px;
    margin: 0;
    color: var(--text-primary);
}

.status {
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 4px 0 0 0;
}

.status-dot {
    width: 8px;
    height: 8px;
    background: var(--success-color);
    border-radius: 50%;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.close-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s ease;
}

.close-btn:hover {
    background: rgba(99, 102, 241, 0.2);
    color: var(--text-primary);
}

/* ============================
   MESSAGES
   ============================ */
.chatbot-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: var(--bg-color);
}

.chatbot-messages::-webkit-scrollbar {
    width: 6px;
}

.chatbot-messages::-webkit-scrollbar-track {
    background: transparent;
}

.chatbot-messages::-webkit-scrollbar-thumb {
    background: var(--surface-light);
    border-radius: 3px;
}

.chatbot-messages::-webkit-scrollbar-thumb:hover {
    background: var(--border-color);
}

.message {
    display: flex;
    gap: 8px;
    animation: message-fade 0.3s ease;
}

@keyframes message-fade {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message-avatar {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--gradient-1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
}

.message.user-message {
    justify-content: flex-end;
}

.message.user-message .message-avatar {
    order: 2;
    background: var(--secondary-color);
}

.message.user-message .message-content {
    order: 1;
}

.message-content {
    max-width: 70%;
    word-wrap: break-word;
}

.message-content p {
    margin: 0;
    padding: 10px 14px;
    border-radius: 12px;
    background: var(--surface-light);
    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.4;
}

.bot-message .message-content p {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
    border: 1px solid var(--border-color);
}

.user-message .message-content p {
    background: var(--primary-color);
    color: white;
}

.welcome-message .message-content p {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.2) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
}

/* ============================
   TYPING INDICATOR
   ============================ */
.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 10px 14px;
}

.typing-indicator.hidden {
    display: none;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: var(--text-secondary);
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        opacity: 0.5;
        transform: translateY(0);
    }
    30% {
        opacity: 1;
        transform: translateY(-10px);
    }
}

/* ============================
   INPUT AREA
   ============================ */
.chatbot-input-area {
    padding: 16px;
    border-top: 1px solid var(--border-color);
    background: var(--surface-color);
}

.input-form {
    display: flex;
    gap: 8px;
    align-items: flex-end;
}

.message-input {
    flex: 1;
    padding: 10px 14px;
    background: var(--bg-color);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
    font-family: inherit;
    transition: all 0.2s ease;
}

.message-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.message-input::placeholder {
    color: var(--text-secondary);
}

.send-btn {
    width: 36px;
    height: 36px;
    padding: 0;
    background: var(--gradient-1);
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.send-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.send-btn:active {
    transform: scale(0.95);
}

.send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: scale(1);
}

.send-btn svg {
    width: 18px;
    height: 18px;
    stroke: currentColor;
}

/* ============================
   RESPONSIVE DESIGN
   ============================ */

/* Tablet (768px and below) */
@media (max-width: 768px) {
    .chatbot-modal {
        width: 90%;
        max-width: 380px;
        height: 500px;
        bottom: 80px;
        right: 12px;
        left: auto;
    }

    .chatbot-toggle {
        bottom: 16px;
        right: 16px;
        width: 56px;
        height: 56px;
    }

    .chat-icon svg {
        width: 24px;
        height: 24px;
    }

    .message-content {
        max-width: 75%;
    }
}

/* Mobile (480px and below) */
@media (max-width: 480px) {
    .chatbot-modal {
        width: calc(100% - 16px);
        max-width: 100%;
        height: 70vh;
        max-height: 600px;
        bottom: 70px;
        right: 8px;
        left: 8px;
        border-radius: 12px;
    }

    .chatbot-toggle {
        bottom: 12px;
        right: 12px;
        width: 52px;
        height: 52px;
    }

    .chat-icon svg {
        width: 22px;
        height: 22px;
    }

    .chatbot-header {
        padding: 16px;
    }

    .header-content h2 {
        font-size: 15px;
    }

    .close-btn {
        width: 28px;
        height: 28px;
        font-size: 20px;
    }

    .chatbot-messages {
        padding: 16px;
        gap: 10px;
    }

    .message-content {
        max-width: 80%;
    }

    .message-content p {
        font-size: 13px;
        padding: 8px 12px;
    }

    .chatbot-input-area {
        padding: 12px;
    }

    .message-input {
        font-size: 13px;
        padding: 8px 12px;
    }

    .send-btn {
        width: 34px;
        height: 34px;
    }

    .send-btn svg {
        width: 16px;
        height: 16px;
    }

    .bot-avatar {
        width: 36px;
        height: 36px;
    }

    .message-avatar {
        width: 24px;
        height: 24px;
        font-size: 12px;
    }
}

/* Small phones (below 360px) */
@media (max-width: 360px) {
    .chatbot-modal {
        height: 80vh;
        max-height: 650px;
    }

    .message-content {
        max-width: 85%;
    }

    .message-content p {
        font-size: 12px;
        padding: 7px 10px;
    }

    .chatbot-messages {
        padding: 12px;
    }
}

/* Dark mode optimization for high contrast */
@media (prefers-contrast: more) {
    .message-content p {
        border: 1px solid var(--border-color);
    }

    .send-btn {
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }

    .pulse {
        animation: none;
        box-shadow: none;
    }
}
'''

# JavaScript File
js_content = '''/* ============================
   CONFIGURATION
   ============================ */
const API_BASE_URL = '/chat';
const USER_ID = 'user_' + Date.now();
const TYPING_DELAY = 1000; // ms

/* ============================
   DOM ELEMENTS
   ============================ */
const chatbotToggle = document.getElementById('chatbotToggle');
const closeChat = document.getElementById('closeChat');
const chatbotModal = document.getElementById('chatbotModal');
const modalOverlay = document.getElementById('modalOverlay');
const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');

/* ============================
   STATE MANAGEMENT
   ============================ */
let isOpen = false;
let isLoading = false;

/* ============================
   EVENT LISTENERS
   ============================ */

// Toggle chatbot
chatbotToggle.addEventListener('click', toggleChatbot);
closeChat.addEventListener('click', closeChatbot);
modalOverlay.addEventListener('click', closeChatbot);

// Chat form
chatForm.addEventListener('submit', handleSendMessage);

// Keyboard shortcut
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
        closeChatbot();
    }
});

/* ============================
   FUNCTIONS
   ============================ */

function toggleChatbot() {
    if (isOpen) {
        closeChatbot();
    } else {
        openChatbot();
    }
}

function openChatbot() {
    isOpen = true;
    chatbotModal.classList.remove('hidden');
    modalOverlay.classList.remove('hidden');
    messageInput.focus();
}

function closeChatbot() {
    isOpen = false;
    chatbotModal.classList.add('hidden');
    modalOverlay.classList.add('hidden');
}

function handleSendMessage(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    if (isLoading) return;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    messageInput.value = '';
    messageInput.focus();

    // Show typing indicator
    showTypingIndicator();

    // Send to API
    sendMessageToAPI(message);
}

function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');

    if (role === 'user') {
        messageDiv.classList.add('user-message');
    } else {
        messageDiv.classList.add('bot-message');
    }

    // Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('message-avatar');

    if (role === 'user') {
        avatarDiv.textContent = '👤';
    } else {
        avatarDiv.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>';
    }

    // Content
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    const paragraph = document.createElement('p');
    paragraph.textContent = text;

    contentDiv.appendChild(paragraph);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

function showTypingIndicator() {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
    isLoading = true;
}

function hideTypingIndicator() {
    typingIndicator.classList.add('hidden');
    isLoading = false;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessageToAPI(message) {
    try {
        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: USER_ID
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Simulate typing delay
        await new Promise(resolve => setTimeout(resolve, TYPING_DELAY));

        hideTypingIndicator();

        // Add bot response
        if (data.response) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Sorry, I couldn\\'t process that request. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error sending message:', error);

        hideTypingIndicator();
        addMessage('Error: Unable to reach the server. Please try again.', 'bot');
    }
}

/* ============================
   INITIALIZATION
   ============================ */

console.log('🤖 Chatbot UI loaded successfully');
console.log('📝 User ID:', USER_ID);
'''

# Write HTML file
with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print('✅ Created: static/index.html')

# Write CSS file
with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write(css_content)
print('✅ Created: static/style.css')

# Write JavaScript file
with open('static/script.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print('✅ Created: static/script.js')

print('\n🎉 All static files created successfully!')
print('📁 Files created in: static/')
print('   - index.html')
print('   - style.css')
print('   - script.js')
print('\n📍 API Endpoint: /chat')
print('🌐 Access at: http://localhost:8000/')
'''