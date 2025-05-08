import sys
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
import chromadb
import uuid

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
        padding: 20px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ced4da;
        padding: 10px;
        font-size: 16px;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 12px;
        border-radius: 15px;
        margin: 5px 10px;
        max-width: 70%;
        word-wrap: break-word;
    }
    .ai-message {
        background-color: #e9ecef;
        color: #333;
        padding: 12px;
        border-radius: 15px;
        margin: 5px 10px;
        max-width: 70%;
        word-wrap: break-word;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: white;
    }
    h1, h3 {
        color: #343a40;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #0056b3;
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
        # st.image("https://via.placeholder.com/150", caption="AI Chatbot")
        st.markdown("### About")
        st.write("This is an AI chatbot based on Utkarsh Patil, powered by Groq and Streamlit.")
        if st.button("Clear Chat History"):
            st.session_state.memory = []
            st.rerun()

    # Main content
    st.title("🤖 AI Chatbot")
    st.markdown("Welcome to the enhanced AI chatbot interface! Ask anything to get started.")

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
                st.markdown("<div style='text-align: center; color: #6c757d;'>No chat history yet. Start the conversation!</div>", unsafe_allow_html=True)

    # User input
    with st.form(key="chat_form", clear_on_submit=True):
        user_query = st.text_input("Your question:", placeholder="Type your message here...")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_query:
            response = query_llama3(user_query)
            st.rerun()

if __name__ == "__main__":
    main()