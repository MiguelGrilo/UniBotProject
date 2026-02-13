import uuid
import requests
import streamlit as st

# Mainpage Configuration
st.set_page_config(page_title="UniBot - Study Assistant", layout="wide")
st.title("UniBot: Study Assistant")

# Creates a unique session ID if it hasn't been created yet
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Uploads Sidebar
with st.sidebar:
    st.header("Documents")
    uploaded_file = st.file_uploader(
        "Load PDF/TXT",
        type=["pdf", "txt"] # "doc", "docx", "ppt", "pptx", "md", "markdown"
    )

    if uploaded_file and st.button("Upload"):
        # Sends to FastAPI
        with st.spinner("Uploading to UniBot..."):
            try:
                # Prepares file to be sent
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post("http://localhost:8000/upload", files=files)

                if response.status_code == 200:
                    st.success(f"{uploaded_file.name} uploaded")
                else:
                    st.error("Upload error")
            except Exception as e:
                st.error("Upload error")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Imput
if prompt := st.chat_input("What do you want to know about your files?"):
    # Stores and shows user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get UniBot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Calls FastAPI (after being questioned)
                response = requests.get(
                    f"http://localhost:8000/ask",
                    params={
                        "question": prompt,
                        "session_id": st.session_state.session_id
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    full_response = data["answer"]

                    st.markdown(full_response)

                    # Show sources if available
                    if data.get("sources"):
                        unique_sources = ", ".join(data["sources"])
                        st.caption(f"Sources: {unique_sources}")

                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error("AI connection error")
            except requests.exceptions.ConnectionError:
                st.error("Connection error. Check if main.py is running")

# RUN: streamlit run gui.py