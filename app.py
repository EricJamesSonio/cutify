from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from jinja2 import ChoiceLoader, FileSystemLoader
import json, random, os, re, difflib, unicodedata
from typing import Optional, List, Tuple, Dict, Any
import datetime
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "chat_log.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user TEXT NOT NULL,
            bot TEXT NOT NULL,
            intent TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB at startup
init_db()


# Serve static files from the root folder
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Set up multiple template folders
app.jinja_loader = ChoiceLoader([
    FileSystemLoader('home'),
    FileSystemLoader('choices'),
    FileSystemLoader('choosen'),
    FileSystemLoader('me')
])

# Routes for HTML pages
@app.route("/")
def home():
    # Redirect to app shell to ensure continuous music across navigation
    return redirect(url_for('app_shell'))

@app.route("/choices")
def choices():
    return render_template("choices_fixed.html")

@app.route("/sadpage")
def sad():
    return render_template("sad.html")

@app.route("/happypage")
def happy():
    return render_template("happy.html")

@app.route("/missingpage")
def missing():
    return render_template("missing.html")

@app.route("/angrypage")
def angry():
    return render_template("angry.html")

@app.route("/confusedpage")
def confused():
    return render_template("confused.html")

@app.route("/hurtpage")
def hurt():
    return render_template("hurt.html")

@app.route("/finepage")
def fine():
    return render_template("fine.html")

@app.route("/me")
def me():
    return render_template("me.html")

@app.route("/visit")
def visit():
    return render_template("visit.html")

# Persistent audio shell route
@app.route("/app")
def app_shell():
    return render_template("app_shell.html")

# New gallery route
@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

# New chat route
@app.route("/chat")
def chat_page():
    return render_template("chat.html")

# Load responses from JSON file
def load_responses():
    try:
        with open('responses.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure structure consistency: keywords dict, default list
            data.setdefault('keywords', {})
            # New: intents list for smarter matching
            data.setdefault('intents', [])
            data.setdefault('default', [
                "Thank you for sharing that with me. I'm always here to listen.",
                "I appreciate you opening up to me, my love.",
                "Your thoughts and feelings matter so much to me.",
                "I'm grateful you trust me with your heart."
            ])
            # Normalize keyword responses to lists
            norm = {}
            for k, v in data['keywords'].items():
                if isinstance(v, list):
                    norm[k] = v
                else:
                    norm[k] = [str(v)]
            data['keywords'] = norm
            return data
    except FileNotFoundError:
        return {
            "keywords": {
                "love": [
                    "I love you so much too! You mean everything to me.",
                    "My heart beats for you every single day.",
                    "You are my world, my everything, my love."
                ],
                "miss": [
                    "I miss you too, babe! Every moment without you feels like forever.",
                    "Distance means nothing when you mean everything to me.",
                    "I'm counting the seconds until I can hold you again."
                ],
                "sad": [
                    "Don't be sad, my love. I'm here for you always.",
                    "Your sadness breaks my heart. Let me comfort you.",
                    "Remember that after every storm comes a rainbow, my dear."
                ],
                "happy": [
                    "I'm so happy to hear that! Your happiness is my happiness.",
                    "Seeing you smile is the best part of my day.",
                    "Your joy fills my heart with so much warmth."
                ],
                "angry": [
                    "Let's talk about it, babe. I want to understand and help.",
                    "I'm here to listen and support you through anything.",
                    "Your feelings are valid, and I want to make things better."
                ],
                "tired": [
                    "You should rest, my love. Sweet dreams when you do!",
                    "Take care of yourself, babe. You deserve all the rest.",
                    "Sleep tight, my angel. I'll be thinking of you."
                ],
                "confused": [
                    "Let me help clear things up for you, my love.",
                    "I'm here to guide you through any confusion.",
                    "Together we can figure anything out, babe."
                ],
                "hurt": [
                    "I'm so sorry you're hurting. I wish I could take your pain away.",
                    "You're not alone in this. I'm here to heal with you.",
                    "My love will help mend whatever is broken."
                ]
            },
            "default": [
                "Thank you for sharing that with me. I'm always here to listen.",
                "I appreciate you opening up to me, my love.",
                "Your thoughts and feelings matter so much to me.",
                "I'm grateful you trust me with your heart."
            ]
        }

def _normalize_text(s: str) -> str:
    # Lowercase, strip accents, keep alnum and spaces, collapse whitespace
    s = s or ''
    s = s.lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()

def _best_keyword_match(message: str, keywords: List[str]) -> Tuple[Optional[str], float]:
    # Returns (best_keyword, score)
    best_key, best_score = None, 0.0
    msg_norm = _normalize_text(message)
    msg_no_space = msg_norm.replace(' ', '')
    words = msg_norm.split()
    for key in keywords:
        key_norm = _normalize_text(key)
        key_no_space = key_norm.replace(' ', '')

        score = 0.0
        # 1) Direct substring match (strong)
        if key_norm and key_norm in msg_norm:
            score = 1.0
        # 2) Space-insensitive approximate
        else:
            score = max(score, _similarity(key_no_space, msg_no_space))
            # 3) Word-level approximate: compare against each word and adjacent pairs
            for i, w in enumerate(words):
                score = max(score, _similarity(key_norm, w))
                if i + 1 < len(words):
                    pair = f"{w} {words[i+1]}"
                    score = max(score, _similarity(key_norm, pair))

        if score > best_score:
            best_key, best_score = key, score

    return best_key, best_score

# --- Intent matching ---
# Keep a tiny memory to avoid immediate repetition per intent
_LAST_INTENT_REPLY: Dict[str, str] = {}

def _match_intent(message: str, intents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the first intent whose any regex pattern matches the message."""
    if not intents:
        return None
    for intent in intents:
        try:
            pats = intent.get('patterns', [])
            for pat in pats:
                if re.search(pat, message, flags=re.IGNORECASE):
                    return intent
        except re.error:
            continue
    return None

def _pick_response(intent: Dict[str, Any]) -> Tuple[str, Optional[str]]:
    """Pick a response (avoid immediate repeat per intent). Also pick optional followup."""
    name = intent.get('name', 'intent')
    responses: List[str] = list(intent.get('responses', []) or [])
    if not responses:
        return "", None
    last = _LAST_INTENT_REPLY.get(name)
    # Try to avoid picking the same as last
    candidates = [r for r in responses if r != last] or responses
    choice = random.choice(candidates)
    _LAST_INTENT_REPLY[name] = choice
    followups = intent.get('followups', []) or []
    follow = random.choice(followups) if followups else None
    return choice, follow





def save_chat(user_message: str, bot_response: str, intent_name: str = None):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO chats (timestamp, user, bot, intent)
            VALUES (?, ?, ?, ?)
        ''', (datetime.datetime.utcnow().isoformat(), user_message, bot_response, intent_name))
        
        conn.commit()
        print(f"Saving chat: {user_message} -> {bot_response}")

        conn.close()
        
    except Exception as e:
        print("Failed to save chat:", e)
        
def get_all_chats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, user, bot, intent FROM chats
        ORDER BY id ASC
    ''')
    rows = c.fetchall()
    conn.close()
    return [
        {"timestamp": ts, "user": u, "bot": b, "intent": i}
        for ts, u, b, i in rows
    ]



# --- Chat API ---
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message', '')
    mood = data.get('mood')
    responses_data = load_responses()

    # 1. Intent-based
    intent = _match_intent(user_message, responses_data.get('intents', []))
    if intent:
        bot_response, followup = _pick_response(intent)
        save_chat(user_message, bot_response, intent_name=intent.get('name'))
        payload = {'response': bot_response, 'status': 'success'}
        if followup: payload['followup'] = followup
        return jsonify(payload)

    # 2. Keyword-based
    keywords = list(responses_data.get('keywords', {}).keys())
    best_key, score = _best_keyword_match(user_message, keywords)
    if best_key and score >= 0.82:
        bot_response = random.choice(responses_data['keywords'][best_key])
    else:
        # 3. Mood/default fallback
        mood_responses = responses_data.get('moodResponses', {}).get(mood) if mood else None
        bot_response = (random.choice(mood_responses['responses']) if mood_responses else
                        random.choice(responses_data['default']))

    save_chat(user_message, bot_response)
    return jsonify({'response': bot_response, 'status': 'success'})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'EJ Bot is running!'})

@app.route("/api/secret_chats")
def secret_chats():
    key = request.args.get("key")
    if key != os.environ.get("ADMIN_KEY", "supersecret"):
        return jsonify({"error": "unauthorized"}), 403
    
    return jsonify(get_all_chats())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
