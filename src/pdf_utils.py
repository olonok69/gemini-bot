import os
import pathlib
import fitz
import uuid
from typing import List
import pymupdf
import base64
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader

import logging


def extract_pdf_images(
    pdf_path, numpages, list_pages, st, file="", num=10, multi=False
):
    """
    extract images from a pdf file
    :param pdf_path: path to pdf file
    :param numpages: number of pages in pdf
    :param list_pages: list of pages to extract
    :return: list of images in bytes
    """
    if "," in list_pages:
        list_pages = list_pages.split(",")
        list_pages = [int(page) - 1 for page in list_pages]
    elif list_pages == "all":
        pass
    elif len(list_pages) == 1 and list_pages.isdigit():
        list_pages = [int(list_pages) - 1]
    else:
        raise ValueError("Invalid value for list_pages")

    pdf_file = open(pdf_path, "rb")
    # placeholders for bytes and file sizes
    images = []
    size_files = []

    if list_pages == "all":
        if multi:
            filepath = f"out/{file}"
        else:
            key_session = f"file_history_{num}"
            filepath = f"out/{st.session_state[key_session]}"
        with open(filepath, "wb") as f:
            f.write(pdf_file.read())
        with open(filepath, "rb") as img:
            images.append(img.read())
        size_files.append(os.path.getsize(filepath))
    else:

        doc = fitz.open(pdf_path)
        # Iterate through the pages of the PDF file
        logging.info(f"number of pages {len(doc)}")
        for page, page_index in zip(doc, range(len(doc))):
            # Get the images on the page
            if page_index in list_pages:
                pix = page.get_pixmap()
                filepath = f"out/page_{page_index}.jpg"
                pix.save(filepath)
                with open(filepath, "rb") as img:
                    images.append(img.read())
                size_files.append(os.path.getsize(filepath))

    return images, size_files


def count_pdf_pages(pdf_path):
    """
    count number of pages in a pdf file
    :param pdf_path: path to pdf file
    :return: number of pages
    """

    doc = fitz.open(pdf_path)

    num_pages = len(doc)

    return num_pages


def upload(list_pages, numpages, st, num: 10):
    """
    upload pdf file and extract images
    :param list_pages: list of pages to extract
    :param numpages: number of pages in pdf
    :param st: session
    :param num: number of session
    :return: list of images in bytes
    """

    parent_path = pathlib.Path(__file__).parent.resolve()
    save_path = os.path.join(parent_path, "data")
    complete_name = st.session_state[f"file_name_{num}"]

    # write list of images to session
    if len(st.session_state[f"list_images_{num}"]) == 0:
        list_images, size_files = extract_pdf_images(
            complete_name, numpages, list_pages, st, complete_name, num=num, multi=False
        )
        st.session_state[f"list_images_{num}"] = list_images
        if list_pages == "all":
            numpages = count_pdf_pages(complete_name)
            total_size = round(sum(size_files) / (1024 * 1024), 2)
            # file name size
            filename = st.session_state[f"file_history_{num}"]
            st.session_state["upload_state"] = (
                f"Ficheros extraído {filename} con y un tamaño total de {total_size} Megabytes"
            )
        else:
            total_size = 0
            paginas_size = ""
            for s in size_files:
                s = round(s / (1024 * 1024), 2)
                paginas_size = paginas_size + f"{s}, "

            total_size = round(sum(size_files) / (1024 * 1024), 2)
            st.session_state[f"upload_state_{num}"] = (
                f"lista de ficheros extraídos {len(list_images) } con tamaños en Megabytes {paginas_size[:-2]} y un tamaño total de {total_size} Megabytes"
            )
    st.session_state[f"value_{num}"] = 3  # pages procesed
    return


def upload_files(st, num: int = 10):
    """
    upload pdfs file in bytes

    :param st: session
    :param num: number of session
    :return: list of images in bytes
    """
    parent_path = pathlib.Path(__file__).parent.parent.resolve()
    save_path = os.path.join(parent_path, "tmp")
    final_list = []
    final_sizes = []
    for file in st.session_state[f"multi_file_name_{num}"]:
        complete_name = os.path.join(save_path, file)
        list_images, size_files = extract_pdf_images(
            complete_name, "all", "all", st, file, num=num, multi=True
        )
        final_list = final_list + list_images
        final_sizes.append(size_files[0])
    total_size = round(sum(final_sizes) / (1024 * 1024), 2)
    st.session_state[f"upload_state_{num}"] = (
        f"Number of Files extracted: {len(final_list)} con un tamaño total de {total_size} Megabytes"
    )
    st.session_state[f"list_images_multi_{num}"] = final_list
    st.session_state[f"value_{num}"] = 3  # pages procesed
    return


def load_file(path):
    # load pdf file and transform into Langchain Documents
    loader = PyMuPDFLoader(path)
    pages = loader.load()
    return pages


def create_documents_metadatas(files: List = [], category: str = "legal"):
    # add documents to Faiss
    documents_all = []
    metadatas_all = []
    ids_all = []

    for file in files:

        pages = load_file(file)
        print(f" Loaded file {file} with {len(pages)} ")
        documents, ids, metadatas = get_docs_to_add_vectorstore(pages, file, category)
        # add documents to collection
        documents_all = documents_all + documents
        metadatas_all = metadatas_all + metadatas
        ids_all = ids_all + ids
    return documents_all, metadatas_all, ids_all


def get_docs_to_add_vectorstore(pages, file, category="legal"):
    # get components to add to Faiis
    documents = []
    ids = []
    metadatas = []

    for page in pages:

        metadatas.append(
            {"page": page.metadata.get("page"), "filename": file, "category": category}
        )
        ids.append(uuid.uuid1().hex)
        documents.append(page.page_content)

    return documents, ids, metadatas


def display_pdf_in_window_bytes(pdf_bytes, width=600, height=400):
    """Displays a PDF from bytes in a smaller window using an iframe."""
    try:
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width}" height="{height}" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")


def display_scanned_pdf_images(pdf_bytes):
    """Displays scanned PDF pages as images in Streamlit."""
    try:
        pdf_document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            st.image(image_bytes, caption=f"Page {page_num + 1}")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def display_scanned_pdf_images_scrollable(pdf_bytes, window_width=800):
    """Displays scanned PDF pages as scrollable images in a single window."""
    try:
        pdf_document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        st.markdown(
            f'<div style="width: {window_width}px; overflow-y: auto;">',
            unsafe_allow_html=True,
        )  # Start scrollable div
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            st.image(
                image_bytes, caption=f"Page {page_num + 1}", use_container_width=True
            )  # use_column_width to scale images to fit div.
        st.markdown("</div>", unsafe_allow_html=True)  # Close scrollable div
    except Exception as e:
        st.error(f"An error occurred: {e}")
