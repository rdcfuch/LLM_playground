from flask import Flask, request, jsonify, render_template
import openai
import ollama
import os

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS
from flask_cors import CORS
CORS(app)

OPENAI_API_KEY="ollama"

# Serve the front page
@app.route('/')
def front_page():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Parse the incoming JSON request
        user_input = request.json.get("message")
        print(user_input)
        if not user_input:
            return jsonify({"error": "No message provided."}), 400

        # Call OpenAI API to get the response from the local Ollama server
        openai.api_base = "http://localhost:11434/"

        response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'user',
                'content': user_input,
                # 'images': ['image.jpg']
            }]
        )

        print(response)

        # response.raise_for_status()
        ai_response = response['message']['content']

        # Extract the text from the OpenAI response

        # Return the AI response as JSON
        return jsonify({"response": ai_response})

    except Exception as e:
        # Handle errors gracefully
        return jsonify({"error": str(e)}), 500


# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

"""
Usage:
1. Create an `index.html` file in the `templates` directory with the desired front page content.
2. Run this script using Python to start the Flask server.
3. Visit `http://localhost:8080/` in your browser to see the front page.
4. Send POST requests to the `/chat` endpoint with JSON data like:

{
  "message": "Hello, how are you?"
}

5. You will receive a response from the Llama model, for example:

{
  "response": "I'm doing well, thank you for asking! How can I assist you today?"
}

Make sure to replace `YOUR_OPENAI_API_KEY` with a valid API key.
"""
