import streamlit as st


def selected_faiss(st, num: int=10):
    st.session_state[f"file_faiss_selected_{num}"] = True


@st.dialog("Visualiza contexto 👇", width="large")
def visualiza_context_faiss(st, out, num: int = 10):
    """
    Function to visualize the context of a document using FAISS.
    Args:
        st (streamlit): Streamlit object.
        out (dict): Dictionary containing the context of the document.
    Returns:
        None

    """
    if f"docs_context_{num}" in st.session_state:
        st.session_state[f"docs_context_{num}"] = out["context"]

    for doc in st.session_state[f"docs_context_{num}"]:
        st.session_state[f"docs_context_names_{num}"].append(
            f"{doc.metadata.get('filename')}_page_{doc.metadata.get('page')}"
        )
    if st.session_state[f"file_faiss_selected_{num}"] == False:
        selector = st.selectbox(
            "Selecciona documento 👇",
            st.session_state[f"docs_context_names_{num}"],
            index=None,
            key=f"select_context_faiss_{num}",
            on_change=selected_faiss,
            args=[st, num],
        )

    if (
        st.session_state[f"file_faiss_selected_{num}"] == True
        and len(st.session_state[f"docs_context_names_{num}"]) > 0
    ):
        with st.expander("Contexto", expanded=True):
            indice = st.session_state[f"docs_context_names_{num}"].index(
                st.session_state[f"select_context_faiss_{num}"]
            )
            st.text_area(
                st.session_state[f"docs_context_names_{num}"][indice],
                height=300,
                key=f"kb_text2_faiss_{num}",
                value=st.session_state[f"docs_context_{num}"][indice].page_content,
            )
            st.session_state[f"file_faiss_selected_{num}"] = False
            if st.button("More"):
                st.session_state[f"file_faiss_selected_{num}"] = True
    return
