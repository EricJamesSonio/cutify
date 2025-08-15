from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from jinja2 import ChoiceLoader, FileSystemLoader
import json, random, os

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
    return render_template("choices.html")

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
# Load responses from JSON file
def load_responses():
    try:
        with open('responses.json', 'r', encoding='utf-8') as f:
            return json.load(f)
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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    mood = data.get('mood', None)
    
    responses_data = load_responses()
    response_text = "Hi Babe! "
    
    # Check for keywords in the message
    found_response = False
    for keyword, responses in responses_data['keywords'].items():
        if keyword in message:
            response_text += random.choice(responses) + " "
            found_response = True
            break
    
    # If no keyword matched, use default response
    if not found_response:
        response_text += random.choice(responses_data['default']) + " "
    
    # Always end with the love signature
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
