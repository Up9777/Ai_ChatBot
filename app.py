import sys
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
import chromadb
import uuid

# Custom CSS for enhanced UI with modern, professional styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e6ecf2 100%);
        padding: 30px;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput input {
        background-color: #d3d3d3 !important;
        color: #000000;
        border-radius: 12px !important;
        border: 1px solid #d1d8e0 !important;
        padding: 12px 15px !important;
        font-size: 15px !important;
    }

    .stTextInput input::placeholder {
        color: #555 !important;
    }

    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 20px;
        border-radius: 16px;
        background-color: #808080;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    .user-message {
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
        color: #2d3748;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 12px;
        max-width: 75%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.5;
    }
    .ai-message {
        background-color: #f1f4f8;
        color: #2d3748;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 12px;
        max-width: 75%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.5;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2d3748 0%, #1a202c 100%);
        color: #e2e8f0;
        padding: 25px;
        border-radius: 0;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
        height: 100vh;
    }
    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 2.2em;
        margin-bottom: 10px;
    }
    h3 {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 1.3em;
        margin-bottom: 15px;
        letter-spacing: 0.5px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 15px;
        font-weight: 500;
        border: none;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        width: 100%;
        margin-top: 20px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0056b3 0%, #003d82 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 91, 187, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    .welcome-text {
        color: #4a5568;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    .chat-placeholder {
        text-align: center;
        color: #718096;
        font-size: 1em;
        padding: 20px;
        font-style: italic;
    }
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f4f8;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: #a0aec0;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #718096;
    }
    .sidebar-image {
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .sidebar-text {
        color: #e2e8f0;
        font-size: 0.95em;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    /* Sidebar button - normal, hover, and active states */
.sidebar .stButton > button {
    background-color: #ffffff !important;
    color: #1a202c !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    border: 1px solid #d1d8e0 !important;
    transition: none !important;
    box-shadow: none !important;
}

/* Prevent hover from changing background or color */
.sidebar .stButton > button:hover,
.sidebar .stButton > button:focus,
.sidebar .stButton > button:active {
    background-color: #ffffff !important;
    color: #1a202c !important;
    border: 1px solid #d1d8e0 !important;
    box-shadow: none !important;
}


    </style>
""", unsafe_allow_html=True)

# Ensure necessary libraries are installed
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ModuleNotFoundError:
    pass

# Initialize Models
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
chat = ChatGroq(
    temperature=0.7,
    model_name="llama3-70b-8192",
    groq_api_key="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"
)
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="ai_knowledge_base")

# Function to query AI model
def query_llama3(user_query):
    system_prompt = "System Prompt: Your AI clone personality based on Utkarsh Patil."

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query)
    ]

    try:
        response = chat.invoke(messages)
        st.session_state.memory.append({"input": user_query, "output": response.content, "id": str(uuid.uuid4())})
        return response.content
    except Exception as e:
        return f"⚠ API Error: {str(e)}"

# Streamlit App
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### About")
        st.markdown("""
            <div class='sidebar-text'>
               This chatbot is an AI-powered conversational tool designed to assist users with a wide range of queries. 
                It leverages advanced natural language processing to provide helpful and accurate responses, 
                offering an engaging and interactive experience for all users.
            </div>
        """, unsafe_allow_html=True)
        if st.button("Clear Chat History"):
            st.session_state.memory = []
            st.rerun()

    # Main content
    st.title("🤖 AI Chatbot")
    st.markdown("<div class='welcome-text'>Welcome to a sleek and modern AI chatbot experience. Ask anything to begin!</div>", unsafe_allow_html=True)

    # Initialize session memory
    if "memory" not in st.session_state:
        st.session_state.memory = []

    # Chat container
    st.markdown("### Conversation")
    with st.container():
        chat_container = st.container()
        with chat_container:
            if st.session_state.memory:
                for chat in st.session_state.memory:
                    # User message
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: flex-end;'>
                            <div class='user-message'>
                                <strong>You:</strong> {chat['input']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    # AI response
                    st.markdown(
                        f"""
                        <div style='display: flex; justify-content: flex-start;'>
                            <div class='ai-message'>
                                <strong>AI:</strong> {chat['output']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<div class='chat-placeholder'>No chat history yet. Start the conversation below!</div>", unsafe_allow_html=True)

    # User input
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input("Your question:", placeholder="Type your message here...")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_query:
            response = query_llama3(user_query)
            st.rerun()

if __name__ == "__main__":
    main()