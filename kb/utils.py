from langchain_community.document_loaders import PyPDFLoader


def load_file(path):
    # load pdf file and transform into Langchain Documents
    loader = PyPDFLoader(path)
    pages = loader.load_and_split()
    return pages


def get_docs_to_add_vectorstore(pages, file, google_ef):
    # get components to add to Chroma
    documents = []
    ids = []
    metadatas = []
    embeddings = []

    for page in pages:
        emb = google_ef([page.page_content])
        embeddings.append(emb[0])
        metadatas.append({"page": page.metadata.get("page"), "filename": file})
        ids.append(uuid.uuid1().hex)
        documents.append(page.page_content)
    return documents, ids, metadatas, embeddings
