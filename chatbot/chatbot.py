# chatbot.py
import os
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

def initialize_groq_chat():
    """
    Initialize the Groq chat client.
    """
    groq_api_key = os.getenv('GROQ_API_KEY')  # Load the GROQ API key from .env
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found. Please set it in the .env file.")
    model = 'llama-3.3-70b-versatile'
    return ChatGroq(groq_api_key=groq_api_key, model_name=model)


def generate_response(chatbot, prompt_template, user_input, memory):
    """
    Generate a response from the chatbot.
    """
    conversation = LLMChain(
        llm=chatbot,
        prompt=prompt_template,
        verbose=False,
        memory=memory,
    )
    return conversation.predict(human_input=user_input)


def construct_prompt(system_prompt, memory):
    """
    Construct the prompt template for the conversation.
    """
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}"),
        ]
    )
