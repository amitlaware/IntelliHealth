import os

# Create directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# base.html
with open('templates/base.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Healthcare Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/style.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="/">AI Healthcare Bot</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    {% if session.get('user_id') %}
                        <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="/chat">Chat</a></li>
                        <li class="nav-item"><a class="nav-link" href="/history">History</a></li>
                        <li class="nav-item"><a class="nav-link text-danger" href="/logout">Logout</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="/login">Login</a></li>
                        <li class="nav-item"><a class="nav-link" href="/register">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    <footer class="text-center mt-5 mb-3 text-muted small">
        <p>Information provided by this chatbot is for general educational purposes only and is not a medical diagnosis or a substitute for professional medical advice.</p>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''')

# index.html
with open('templates/index.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<div class="px-4 py-5 my-5 text-center">
    <h1 class="display-5 fw-bold text-primary">AI Healthcare Bot</h1>
    <div class="col-lg-6 mx-auto">
        <p class="lead mb-4">Get quick access to general healthcare information using AI and Natural Language Processing.</p>
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
            <a href="/login" class="btn btn-primary btn-lg px-4 gap-3">Start Chat</a>
        </div>
    </div>
</div>
{% endblock %}''')

# login.html
with open('templates/login.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Login</h3>
                <form id="loginForm">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" required>
                    </div>
                    <div id="errorMsg" class="text-danger mb-3 d-none"></div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
            </div>
        </div>
    </div>
</div>
<script>
document.getElementById('loginForm').onsubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: document.getElementById('username').value,
            password: document.getElementById('password').value
        })
    });
    if(res.ok) window.location.href = '/dashboard';
    else {
        const data = await res.json();
        document.getElementById('errorMsg').textContent = data.error;
        document.getElementById('errorMsg').classList.remove('d-none');
    }
};
</script>
{% endblock %}''')

# register.html
with open('templates/register.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Register</h3>
                <form id="registerForm">
                    <div class="mb-3">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" required>
                    </div>
                    <div id="errorMsg" class="text-danger mb-3 d-none"></div>
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                </form>
            </div>
        </div>
    </div>
</div>
<script>
document.getElementById('registerForm').onsubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value
        })
    });
    if(res.ok) window.location.href = '/login';
    else {
        const data = await res.json();
        document.getElementById('errorMsg').textContent = data.error;
        document.getElementById('errorMsg').classList.remove('d-none');
    }
};
</script>
{% endblock %}''')

# dashboard.html
with open('templates/dashboard.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<h2>Welcome, {{ session['username'] }}</h2>
<div class="mt-4">
    <a href="/chat" class="btn btn-success">Start New Chat</a>
    <a href="/history" class="btn btn-secondary">View History</a>
</div>
{% endblock %}''')

# chat.html
with open('templates/chat.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<div class="card shadow-sm chat-card">
    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <span>AI Healthcare Assistant</span>
        <span class="badge bg-light text-dark">AI Information</span>
    </div>
    <div class="card-body chat-box" id="chatBox">
        <div class="text-center text-muted mb-3"><small>Conversation Started</small></div>
    </div>
    <div class="card-footer">
        <form id="chatForm" class="d-flex">
            <input type="hidden" id="convId" value="">
            <input type="text" id="chatInput" class="form-control me-2" placeholder="Type a message..." required autocomplete="off">
            <button type="submit" class="btn btn-primary">Send</button>
        </form>
    </div>
</div>

<script src="/static/js/chat.js"></script>
{% endblock %}''')

# history.html
with open('templates/history.html', 'w') as f:
    f.write('''{% extends "base.html" %}
{% block content %}
<h2>Conversation History</h2>
<div id="historyList" class="list-group mt-3"></div>
<script>
window.onload = async () => {
    const res = await fetch('/api/conversations');
    const convs = await res.json();
    const list = document.getElementById('historyList');
    convs.forEach(c => {
        list.innerHTML += `<a href="/chat?id=${c.id}" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
            ${c.title} <small>${new Date(c.created_at).toLocaleString()}</small>
        </a>`;
    });
};
</script>
{% endblock %}''')

# CSS
with open('static/css/style.css', 'w') as f:
    f.write('''
.chat-card { max-width: 800px; margin: 0 auto; height: 75vh; display: flex; flex-direction: column; }
.chat-box { flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; padding: 20px; }
.msg { padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; max-width: 75%; }
.msg-user { background-color: #007bff; color: white; align-self: flex-end; border-bottom-right-radius: 0; }
.msg-bot { background-color: #f1f1f1; color: #333; align-self: flex-start; border-bottom-left-radius: 0; }
.msg-urgent { background-color: #dc3545; color: white; border: 2px solid #ffc107; }
''')

# JS
with open('static/js/chat.js', 'w') as f:
    f.write('''
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
''')
