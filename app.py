from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from jinja2 import ChoiceLoader, FileSystemLoader
import json, random, os, re, difflib, unicodedata
from typing import Optional, List, Tuple

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
    return render_template("home.html")

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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    raw_message = data.get('message', '')
    mood = data.get('mood', None)

    responses_data = load_responses()
    response_text = "Hi Babe! "

    # Smart keyword matching with typo tolerance
    keywords = list(responses_data['keywords'].keys())
    best_key, score = _best_keyword_match(raw_message, keywords)

    # Thresholds: exact/substring -> 1.0, fuzzy accept >= 0.82
    if best_key is not None and score >= 0.82:
        responses = responses_data['keywords'][best_key]
        response_text += random.choice(responses) + " "
    else:
        response_text += random.choice(responses_data['default']) + " "

    # Signature
    response_text += "ILOVEYOUUUUVERYMUCH BABE!"

    return jsonify({
        'response': response_text,
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'EJ Bot is running!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
