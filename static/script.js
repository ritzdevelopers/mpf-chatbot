
const USER_ID = (() => {
  const key = 'mpf_chat_user_id';
  let id = localStorage.getItem(key);
  if (!id) {
    id = 'user_' + Date.now();
    localStorage.setItem(key, id);
  }
  return id;
})();
let chatOpen = false;

// ---- Open / Close ----

function openChat() {
  chatOpen = true;
  document.getElementById('chatWindow').classList.add('open');
  document.getElementById('chatFab').classList.add('open');
  document.getElementById('chatOverlay').classList.add('active');
  setTimeout(() => document.getElementById('chatInput').focus(), 350);
}

function closeChat() {
  chatOpen = false;
  document.getElementById('chatWindow').classList.remove('open');
  document.getElementById('chatFab').classList.remove('open');
  document.getElementById('chatOverlay').classList.remove('active');
}

// ---- Utilities ----

function getTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  const el = document.getElementById('chatMessages');
  el.scrollTop = el.scrollHeight;
}

function appendMessage(role, text) {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = `
    <div class="msg-bubble">${formatText(text)}</div>
    <span class="msg-time">${getTime()}</span>
  `;
  msgs.appendChild(div);
  scrollToBottom();
}

function formatText(text) {
  if (text == null) return '';
  const s = typeof text === 'string' ? text : String(text);
  return s
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
}

function showTyping() {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'msg bot';
  div.innerHTML = `
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  msgs.appendChild(div);
  scrollToBottom();
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

// ---- Send ----

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const btn = document.getElementById('sendBtn');
  const message = input.value.trim();
  if (!message) return;

  // Hide quick chips after first message
  const chips = document.querySelector('.quick-chips');
  if (chips) chips.style.display = 'none';

  input.value = '';
  btn.disabled = true;
  appendMessage('user', message);
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: USER_ID })
    });
    const data = await res.json();
    removeTyping();
    if (!res.ok) {
      appendMessage('bot', data.detail || '⚠️ Something went wrong. Please try again.');
      return;
    }
    const reply = data.response != null
      ? (typeof data.response === 'string' ? data.response : String(data.response))
      : '';
    if (!reply) {
      appendMessage('bot', '⚠️ Empty response from server. Please try again.');
      return;
    }
    appendMessage('bot', reply);
  } catch (err) {
    removeTyping();
    console.error(err);
    appendMessage('bot', '⚠️ Sorry, I could not connect. Please try again.');
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function sendQuick(text) {
  document.getElementById('chatInput').value = text;
  sendMessage();
}

// ---- Enter key ----
document.getElementById('chatInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) sendMessage();
});
