import streamlit as st


def selected_faiss(st):
    st.session_state["file_faiss_selected"] = True


@st.experimental_dialog("Visualiza contexto 👇", width="large")
def visualiza_context_faiss(st, out):
    """
    Function to visualize the context of a document using FAISS.
    Args:
        st (streamlit): Streamlit object.
        out (dict): Dictionary containing the context of the document.
    Returns:
        None

    """
    if "docs_context" in st.session_state:
        st.session_state["docs_context"] = out["context"]

    for doc in st.session_state["docs_context"]:
        st.session_state["docs_context_names"].append(
            f"{doc.metadata.get('filename')}_page_{doc.metadata.get('page')}"
        )
    if st.session_state["file_faiss_selected"] == False:
        selector = st.selectbox(
            "Selecciona documento 👇",
            st.session_state["docs_context_names"],
            index=None,
            key="select_context_faiss",
            on_change=selected_faiss,
            args=[st],
        )

    if (
        st.session_state["file_faiss_selected"] == True
        and len(st.session_state["docs_context_names"]) > 0
    ):
        with st.expander("Contexto", expanded=True):
            indice = st.session_state["docs_context_names"].index(
                st.session_state["select_context_faiss"]
            )
            st.text_area(
                st.session_state["docs_context_names"][indice],
                height=300,
                key="kb_text2_faiss",
                value=st.session_state["docs_context"][indice].page_content,
            )
            st.session_state["file_faiss_selected"] = False
            if st.button("More"):
                st.session_state["file_faiss_selected"] = True
    return
