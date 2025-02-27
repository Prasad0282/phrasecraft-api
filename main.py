import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot.prompts import get_grammar_prompt
from chatbot.chatbot import initialize_groq_chat, construct_prompt, generate_response
from chatbot.utils import load_environment_variables
from langchain.chains.conversation.memory import ConversationBufferMemory
from chatbot.utils import load_environment_variables

load_environment_variables()



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

chat_memories = {}
groq_chat = None

# Define the bot configuration with topics and routes
BOT_CONFIG = {
    "Nouns": "/nouns/process",
    "Pronouns": "/pronouns/analyze",
    "Verbs": "/verbs/process",
    "Adjectives": "/adjectives/classify",
    "Adverbs": "/adverbs/identify",
    "Conjunctions": "/conjunctions/handle",
    "Prepositions": "/prepositions/analyze",
    "Interjections": "/interjections/respond",
    "Compound Sentences": "/compound-sentences/process",
    "Complex Sentences": "/complex-sentences/process",
    "Articles": "/articles/identify",
    "Subject-Verb Agreement": "/subject-verb/process",
    "Determiners & Quantifiers": "/determiners-quantifiers/identify",
    "WH - Question Words": "/wh-questions/handle",
    "Tenses": "/tenses/process",
    "Active and Passive Voice": "/voice/analyze"
}

# Initialize Groq Chat
def setup():
    global groq_chat
    load_environment_variables()
    groq_chat = initialize_groq_chat()

setup()

@app.route("/")
def home():
    return send_from_directory(directory=".", path="index.html")

@app.route("/api/topics", methods=["GET"])
def get_topics():
    grammar_topics = list(BOT_CONFIG.keys())
    return jsonify({"topics": grammar_topics})

@app.route("/api/chat", methods=["POST"])
def chat():
    global chat_memories, groq_chat

    data = request.json
    topic = data.get("topic")
    user_input = data.get("message")

    if not topic or not user_input:
        return jsonify({"error": "Topic and message are required"}), 400

    # Ensure the topic exists in the bot configuration
    if topic not in BOT_CONFIG:
        return jsonify({"error": f"Topic '{topic}' is not supported"}), 404

    # Initialize memory for the topic if not already done
    if topic not in chat_memories:
        chat_memories[topic] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    memory = chat_memories[topic]
    system_prompt = get_grammar_prompt(topic)

    if user_input.lower() == "exit":
        return jsonify({"response": "Goodbye! Keep practicing and improving!"})

    # Construct prompt and generate response
    prompt = construct_prompt(system_prompt, memory)
    response = generate_response(groq_chat, prompt, user_input, memory)

    # Add messages to memory
    memory.chat_memory.add_user_message(user_input)
    memory.chat_memory.add_ai_message(response)

    return jsonify({"response": response})

@app.route("/api/history", methods=["GET"])
def get_history():
    topic = request.args.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    if topic not in chat_memories:
        return jsonify({"history": []})

    memory = chat_memories[topic]
    history = memory.chat_memory.messages

    formatted_history = [
        {"sender": "You", "message": msg.content} if msg.type == "user" else {"sender": "Chatbot", "message": msg.content}
        for msg in history
    ]

    return jsonify({"history": formatted_history})

@app.route("/api/clear_memory", methods=["POST"])
def clear_memory():
    topic = request.json.get("topic")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    if topic in chat_memories:
        del chat_memories[topic]

    return jsonify({"message": "Memory cleared for topic."})

if __name__ == "__main__":
     app.run(debug=True,port=5000)
