import streamlit as st
import state
from groq import Groq

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

import hashlib  # Add this import


# ========== NEW CONTEXT BUFFER CLASSES ==========
class ConversationBuffer:
    def __init__(self, max_length=3):
        self.history = []
        self.max_length = max_length
        self.cached_docs = {}

    def add_interaction(self, query, response, docs):
        doc_hash = hashlib.sha256("".join([d.page_content for d in docs]).encode()).hexdigest()
        self.history.append({
            'query': query,
            'response': response,
            'doc_hash': doc_hash
        })
        self.cached_docs[doc_hash] = docs
        if len(self.history) > self.max_length:
            oldest = self.history.pop(0)
            if oldest['doc_hash'] not in [h['doc_hash'] for h in self.history]:
                del self.cached_docs[oldest['doc_hash']]



# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

# Define the path to the pre-trained model you want to use
modelPath = "sentence-transformers/all-MiniLM-l6-v2"

# Create a dictionary with model configuration options, specifying to use the CPU for computations
model_kwargs = {'device':'cpu'}

# Create a dictionary with encoding options, specifically setting 'normalize_embeddings' to False
encode_kwargs = {'normalize_embeddings': False}

embeddings = HuggingFaceEmbeddings(
    model_name=modelPath,     # Provide the pre-trained model's path
    model_kwargs=model_kwargs, # Pass the model configuration options
    encode_kwargs=encode_kwargs # Pass the encoding options
)

# connect to the chromadb
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH, 
)

# Set up the vectorstore to be the retriever
num_results = 5
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})



def is_follow_up(query):
    query = query.lower()
    return any(term in query for term in [
        'more about', 'what about', 'explain', 'how about', 'tell me', 'that'
    ])

def extract_key_terms(text):
    # Simple keyword extraction (can be enhanced with NLP later)
    return list(set(text.lower().split()[:5]))  # First 5 unique words



def display_messages(app_name):
    """Display chat messages from session state."""
    for message in st.session_state.messages:
        if message["role"] != "system":
            role_name = "user" if message["role"] == "user" else app_name
            with st.chat_message(role_name):
                st.markdown(message["content"])

# ========== MODIFIED GET_AI_RESPONSE ==========
def get_ai_response(prompt, client, model, additional_instructions:str = ""):
    # Initialize conversation buffer in session state
    if 'conv_buffer' not in st.session_state:
        st.session_state.conv_buffer = ConversationBuffer()
    
    knowledge = ""
    combined_docs = []

    if prompt:
        # Context-aware retrieval
        if st.session_state.conv_buffer.history and is_follow_up(prompt):
            # Get context terms from previous responses
            context_terms = []
            for entry in st.session_state.conv_buffer.history:
                context_terms.extend(extract_key_terms(entry['response']))
            
            # Boost context terms in search
            boosted_query = f"{prompt} {' '.join(context_terms)}"
            docs = retriever.invoke(boosted_query)[:num_results]
            
            # Combine with previous docs
            previous_docs = []
            for h in st.session_state.conv_buffer.cached_docs.values():
                previous_docs.extend(h)
            combined_docs = list({d.page_content: d for d in docs + previous_docs}.values())[:num_results]
        else:
            # First-time query
            docs = retriever.invoke(prompt)[:num_results]
            combined_docs = docs
        
        # Build knowledge string
        for doc in combined_docs:
            knowledge += doc.page_content + "\n\n"

    """Fetch AI response from Groq API."""
    history = st.session_state.messages[-12:]
    system_prompt = state.get_system_prompt()
    
    # Modified message structure
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Relevant knowledge:\n{knowledge}"}  # More natural phrasing
    ] + history

    if additional_instructions:
        messages.append({"role": "system", "content": additional_instructions})

    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )

        response_container = st.empty()
        full_response = ""

        for chunk in response_stream:
            text = chunk.choices[0].delta.content
            if text:
                full_response += text
                response_container.markdown(full_response)

        # Update conversation buffer after successful response
        if prompt and combined_docs:
            st.session_state.conv_buffer.add_interaction(prompt, full_response, combined_docs)

        return full_response.strip()
    except Exception as e:
        st.error("Oops! Something went wrong. Please try again.")
        print(f"Error in AI response: {e}")
        return None

# ========== MODIFIED HANDLE_USER_INPUT ==========
def handle_user_input(client, model):
    """Handle user input and get AI response."""
    
    if prompt := st.chat_input("Ask a question", max_chars=500):
        # Clear previous conversation buffer if new topic
        if not is_follow_up(prompt) and st.session_state.conv_buffer.history:
            st.session_state.conv_buffer = ConversationBuffer()


        # Save the AI first message now that user has started the conversation
        if st.session_state.unsaved_ai_message:
            state.guest_save_message(state.get_guest_id(), "assistant", st.session_state.unsaved_ai_message)
            st.session_state.unsaved_ai_message = None

        with st.chat_message("user"):
            st.markdown(prompt)

        # Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        state.guest_save_message(state.get_guest_id(), "user", prompt)

        # Get AI response
        with st.chat_message("assistant"):
            response = get_ai_response(prompt, client, model)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.guest_save_message(state.get_guest_id(), "assistant", response)


def show_chat_page():
    """Main function to render the chat page."""
    app_name = st.secrets["APP_NAME"]
    model = st.secrets["GROQ_MODEL"]
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    st.title(app_name)

    # Display messages and handle input
    display_messages(app_name)
    

    if not st.session_state.welcome_message_is_sent:
        instruction = f"Introduce yourself and your purpose."
        st.session_state.welcome_message_is_sent = True

        with st.chat_message("assistant"):
            response = get_ai_response("", client, model, additional_instructions=instruction)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                state.unsaved_ai_message = response

                
    handle_user_input(client, model)