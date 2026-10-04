from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from services.chatbot_service import ChatbotService
from models.models import db, init_db, User, Conversation, Message
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///healthcare.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

chatbot = ChatbotService()
init_db(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized. Please login."}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/chat")
@login_required
def chat_page():
    return render_template("chat.html")

@app.route("/history")
@login_required
def history_page():
    return render_template("history.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400
        
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Username or email already exists."}), 409
        
    try:
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error."}), 500

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"message": "Login successful."}), 200
    
    return jsonify({"error": "Invalid credentials."}), 401

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/api/conversations", methods=["POST"])
@login_required
def create_conversation():
    try:
        conv = Conversation(user_id=session['user_id'], title="New Conversation")
        db.session.add(conv)
        db.session.commit()
        return jsonify({"id": conv.id, "title": conv.title, "created_at": conv.created_at}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error."}), 500

@app.route("/api/conversations", methods=["GET"])
@login_required
def get_conversations():
    convs = Conversation.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{"id": c.id, "title": c.title, "created_at": c.created_at} for c in convs]), 200

@app.route("/api/conversations/<int:id>", methods=["DELETE"])
@login_required
def delete_conversation(id):
    conv = Conversation.query.filter_by(id=id, user_id=session['user_id']).first()
    if not conv:
        return jsonify({"error": "Conversation not found."}), 404
    try:
        db.session.delete(conv)
        db.session.commit()
        return jsonify({"message": "Conversation deleted."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error."}), 500

@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    conv_id = request.args.get("conversation_id", type=int)
    if not conv_id:
        return jsonify({"error": "conversation_id required."}), 400
        
    conv = Conversation.query.filter_by(id=conv_id, user_id=session['user_id']).first()
    if not conv:
        return jsonify({"error": "Conversation not found."}), 404
        
    messages = Message.query.filter_by(conversation_id=conv.id).order_by(Message.timestamp.asc()).all()
    return jsonify([{
        "id": m.id,
        "sender": m.sender,
        "message": m.message,
        "intent": m.intent,
        "confidence": m.confidence,
        "timestamp": m.timestamp
    } for m in messages]), 200

@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    conv_id = data.get("conversation_id")
    
    if not message:
        return jsonify({"error": "Please enter a message."}), 400
    if not conv_id:
        return jsonify({"error": "Please provide a conversation_id."}), 400
        
    conv = Conversation.query.filter_by(id=conv_id, user_id=session['user_id']).first()
    if not conv:
        return jsonify({"error": "Conversation not found."}), 404
        
    bot_response = chatbot.respond(message)
    
    try:
        user_msg = Message(
            conversation_id=conv.id, 
            sender="user", 
            message=message
        )
        bot_msg = Message(
            conversation_id=conv.id, 
            sender="bot", 
            message=bot_response.get("response", ""),
            intent=bot_response.get("intent", ""),
            confidence=bot_response.get("confidence")
        )
        db.session.add(user_msg)
        db.session.add(bot_msg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error."}), 500
        
    return jsonify({
        "conversation_id": conv.id,
        "intent": bot_response.get("intent"),
        "confidence": bot_response.get("confidence"),
        "urgent": bot_response.get("urgent"),
        "response": bot_response.get("response")
    })

if __name__ == "__main__":
    app.run(debug=True)
