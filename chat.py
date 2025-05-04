from flask import Flask, request, jsonify
import os
import requests
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Fetch Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables!")

# Gemini API URL
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"


# Function to get reply from Gemini
def get_gemini_reply(message):
    payload = {
        "contents": [
            {
                "parts": [{"text": message}]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    params = {
        "key": GEMINI_API_KEY
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        print("📨 Gemini API status:", response.status_code)
        print("📨 Gemini API raw response:", response.text)

        if response.status_code != 200:
            return None, f"Gemini API failed with status code {response.status_code}"

        data = response.json()
        reply = data['candidates'][0]['content']['parts'][0]['text']
        return reply, None

    except (KeyError, IndexError, TypeError) as e:
        print("❌ Error parsing Gemini response:", str(e))
        return None, "Gemini response format error"

    except Exception as e:
        print("❌ Gemini API request exception:", str(e))
        return None, "Unexpected error calling Gemini API"

# Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        print("📩 Received message from frontend:", data)

        user_message = data.get("message")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        reply, error = get_gemini_reply(user_message)

        if error:
            print("⚠️ Gemini processing error:", error)
            return jsonify({"response": "Sorry, something went wrong while processing your request."}), 500

        return jsonify({"response": reply})

    except Exception as e:
        print("❌ Server exception:", str(e))
        return jsonify({"response": "Internal server error"}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)

