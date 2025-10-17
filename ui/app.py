# ui/app.py
import streamlit as st
import requests
import json

# Page config
st.set_page_config(page_title="RAG Knowledge Base", page_icon="🧠", layout="wide")

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


def main():
    st.title("🧠 RAG Knowledge Base")
    st.markdown("Advanced Retrieval-Augmented Generation System")

    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page", ["Query", "Document Ingestion", "System Stats"]
        )

    if page == "Query":
        show_query_page()
    elif page == "Document Ingestion":
        show_ingestion_page()
    elif page == "System Stats":
        show_stats_page()


def show_query_page():
    st.header("Ask Questions")

    # Query input
    question = st.text_area(
        "Enter your question:", placeholder="What would you like to know?", height=100
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        max_results = st.slider("Max Results", 1, 20, 10)
        include_sources = st.checkbox("Include Sources", value=True)

    if st.button("Ask Question", type="primary"):
        if question:
            with st.spinner("Searching knowledge base..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/query/ask",
                        json={
                            "question": question,
                            "max_results": max_results,
                            "include_sources": include_sources,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:
                        result = response.json()

                        st.subheader("Answer")
                        st.write(result["answer"])

                        if include_sources and result["sources"]:
                            st.subheader("Sources")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(f"Source {i}"):
                                    st.json(source)

                        st.subheader("Metadata")
                        st.json(result["metadata"])

                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")
                    st.warning("Make sure the API server is running on localhost:8000")
        else:
            st.warning("Please enter a question")


def show_ingestion_page():
    st.header("Document Ingestion")

    tab1, tab2 = st.tabs(["Upload File", "Add Text"])

    with tab1:
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file", type=["txt", "pdf", "docx", "md"]
        )

        if uploaded_file is not None:
            if st.button("Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": uploaded_file}
                        response = requests.post(
                            f"{API_BASE_URL}/ingest/document", files=files, timeout=60
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(result["message"])
                            st.json(result)
                        else:
                            st.error(f"API Error: {response.status_code}")
                            st.write(response.text)

                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")

    with tab2:
        st.subheader("Add Text Content")
        text_content = st.text_area("Enter text content:", height=200)

        metadata_json = st.text_area(
            "Metadata (JSON format):", value='{"source": "manual_input"}', height=100
        )

        if st.button("Process Text", type="primary"):
            if text_content:
                with st.spinner("Processing text..."):
                    try:
                        metadata = json.loads(metadata_json) if metadata_json else {}

                        response = requests.post(
                            f"{API_BASE_URL}/ingest/text",
                            json={"text": text_content, "metadata": metadata},
                            timeout=30,
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(result["message"])
                            st.json(result)
                        else:
                            st.error(f"API Error: {response.status_code}")

                    except json.JSONDecodeError:
                        st.error("Invalid JSON in metadata field")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Connection error: {e}")
            else:
                st.warning("Please enter some text content")


def show_stats_page():
    st.header("System Statistics")

    if st.button("Refresh Stats"):
        with st.spinner("Loading statistics..."):
            try:
                response = requests.get(f"{API_BASE_URL}/ingest/stats", timeout=10)

                if response.status_code == 200:
                    stats = response.json()

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Documents", stats.get("total_documents", 0))
                        st.metric("Total Chunks", stats.get("total_chunks", 0))

                    with col2:
                        st.metric(
                            "Vector Store Count", stats.get("vector_store_count", 0)
                        )

                    with col3:
                        st.metric("Graph Nodes", stats.get("graph_nodes", 0))
                        st.metric(
                            "Graph Relationships", stats.get("graph_relationships", 0)
                        )

                else:
                    st.error(f"API Error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")


if __name__ == "__main__":
    main()
