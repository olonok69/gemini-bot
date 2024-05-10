import os
import pathlib
import fitz


def extract_pdf_images(pdf_path, numpages, list_pages, st, file="", multi=False):
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
            filepath = f"out/{st.session_state['file_history']}"
        with open(filepath, "wb") as f:
            f.write(pdf_file.read())
        with open(filepath, "rb") as img:
            images.append(img.read())
        size_files.append(os.path.getsize(filepath))
    else:

        doc = fitz.open(pdf_path)
        # Iterate through the pages of the PDF file
        print(f"number of pages {len(doc)}")
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


def upload(list_pages, numpages, st):
    """
    upload pdf file and extract images
    :param list_pages: list of pages to extract
    :param numpages: number of pages in pdf
    :return: list of images in bytes
    """

    parent_path = pathlib.Path(__file__).parent.resolve()
    save_path = os.path.join(parent_path, "data")
    complete_name = st.session_state["file_name"]

    # write list of images to session
    if len(st.session_state["list_images"]) == 0:
        list_images, size_files = extract_pdf_images(
            complete_name, numpages, list_pages, st, complete_name, multi=False
        )
        st.session_state["list_images"] = list_images
        if list_pages == "all":
            numpages = count_pdf_pages(complete_name)
            total_size = round(sum(size_files) / (1024 * 1024), 2)
            st.session_state["upload_state"] = (
                f"Ficheros extraído {st.session_state['file_history']} con y un tamaño total de {total_size} Megabytes"
            )
        else:
            total_size = 0
            paginas_size = ""
            for s in size_files:
                s = round(s / (1024 * 1024), 2)
                paginas_size = paginas_size + f"{s}, "

            total_size = round(sum(size_files) / (1024 * 1024), 2)
            st.session_state["upload_state"] = (
                f"lista de ficheros extraídos {len(list_images) } con tamaños en Megabytes {paginas_size[:-2]} y un tamaño total de {total_size} Megabytes"
            )
    st.session_state.value = 3  # pages procesed
    return


def upload_files(st):
    """
    upload pdfs file in bytes

    :param st: session
    :return: list of images in bytes
    """
    parent_path = pathlib.Path(__file__).parent.parent.resolve()
    save_path = os.path.join(parent_path, "tmp")
    final_list = []
    final_sizes = []
    for file in st.session_state["multi_file_name"]:
        complete_name = os.path.join(save_path, file)
        list_images, size_files = extract_pdf_images(
            complete_name, "all", "all", st, file, multi=True
        )
        final_list = final_list + list_images
        final_sizes.append(size_files[0])
    total_size = round(sum(final_sizes) / (1024 * 1024), 2)
    st.session_state["upload_state"] = (
        f"Number of Files extracted: {len(final_list)} con un tamaño total de {total_size} Megabytes"
    )
    st.session_state["list_images_multi"] = final_list
    st.session_state.value = 3  # pages procesed
    return
