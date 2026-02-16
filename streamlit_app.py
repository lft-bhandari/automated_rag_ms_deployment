import json
from typing import Any

import requests
import streamlit as st


def extract_chat_response(response: requests.Response) -> str:
    """Normalize the API response to plain text for display."""
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or "(empty response)"

    if isinstance(payload, str):
        return payload

    if isinstance(payload, dict):
        for key in ("response", "answer", "message"):
            if key in payload:
                return str(payload[key])
        return json.dumps(payload, indent=2)

    return str(payload)


def error_payload_to_text(response: requests.Response) -> str:
    try:
        payload = response.json()
        return json.dumps(payload, indent=2)
    except ValueError:
        return response.text.strip()


def render_error_payload(response: requests.Response) -> None:
    details = error_payload_to_text(response)
    if details:
        st.code(details)


st.set_page_config(page_title="Document RAG Frontend", page_icon="📚", layout="wide")

st.title("📚 Document Upload + Chat")
st.caption("Streamlit UI for `/document/upload-index` and `/document/doc-chat` endpoints.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("API Settings")
    api_base_url = st.text_input(
        "FastAPI base URL",
        value="http://localhost:8000",
        help="Base URL where the FastAPI service is running.",
    ).rstrip("/")

    upload_endpoint = f"{api_base_url}/document/upload-index"
    chat_endpoint = f"{api_base_url}/document/doc-chat"

    st.markdown("---")
    st.write("**Resolved endpoints**")
    st.code(f"POST {upload_endpoint}\nPOST {chat_endpoint}")

upload_tab, chat_tab = st.tabs(["Upload & Index", "Document Chat"])

with upload_tab:
    st.subheader("Upload JSON documents")
    st.write(
        "Upload a `.json` file that contains a list of documents with `content` and optional `metadata`."
    )

    uploaded_file = st.file_uploader("Select JSON file", type=["json"])
    batch_size = st.number_input("Batch size", min_value=1, max_value=100, value=10, step=1)

    if st.button("Upload & Index", type="primary", disabled=uploaded_file is None):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/json")}
        params = {"batch_size": int(batch_size)}

        with st.spinner("Uploading and indexing documents..."):
            try:
                response = requests.post(
                    upload_endpoint,
                    files=files,
                    params=params,
                    timeout=120,
                )

                if response.ok:
                    data: dict[str, Any] = response.json()
                    st.success("Upload and indexing completed.")
                    st.json(data)
                else:
                    st.error(f"Upload failed ({response.status_code}).")
                    render_error_payload(response)

            except requests.RequestException as exc:
                st.error(f"Request error: {exc}")

with chat_tab:
    st.subheader("Ask questions against indexed documents")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a question about your documents")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        chat_endpoint,
                        params={"user_query": prompt},
                        timeout=120,
                    )

                    if response.ok:
                        answer = extract_chat_response(response)
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    else:
                        error_message = f"Chat failed ({response.status_code})."
                        st.error(error_message)
                        details = error_payload_to_text(response)
                        if details:
                            st.code(details)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": error_message}
                        )

                except requests.RequestException as exc:
                    error_message = f"Request error: {exc}"
                    st.error(error_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_message}
                    )
