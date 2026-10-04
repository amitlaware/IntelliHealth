
let convId = new URLSearchParams(window.location.search).get('id');
const chatBox = document.getElementById('chatBox');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');

async function init() {
    if(!convId) {
        const res = await fetch('/api/conversations', {method: 'POST'});
        const data = await res.json();
        convId = data.id;
    } else {
        const res = await fetch(`/api/history?conversation_id=${convId}`);
        const msgs = await res.json();
        msgs.forEach(m => addMessage(m.message, m.sender, m.urgent));
    }
}

function addMessage(text, sender, urgent=false) {
    const div = document.createElement('div');
    div.className = `msg msg-${sender} ${urgent ? 'msg-urgent' : ''}`;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.onsubmit = async (e) => {
    e.preventDefault();
    const msg = chatInput.value;
    chatInput.value = '';
    addMessage(msg, 'user');
    
    const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg, conversation_id: convId})
    });
    
    if(res.ok) {
        const data = await res.json();
        addMessage(data.response, 'bot', data.urgent);
    } else {
        addMessage("Sorry, an error occurred.", 'bot', true);
    }
};

init();
