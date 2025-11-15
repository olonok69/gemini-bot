import base64
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components


def render_pdf(
    binary: bytes,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
    key: Optional[str] = None,
    title: str = "PDF preview",
) -> None:
    """Render a PDF inline via an iframe without relying on custom components.

    Args:
        binary: Raw PDF bytes to embed.
        width: Width in pixels for the iframe (defaults to 100% column width).
        height: Height in pixels for the iframe (defaults to 600px).
        key: Optional Streamlit component key to help avoid redraw collisions.
        title: Accessible title/aria label for the iframe.
    """

    if binary is None:
        st.info("No PDF available to display yet.")
        return

    iframe_width = width or "100%"
    iframe_height = height or 600

    base64_pdf = base64.b64encode(binary).decode("utf-8")
    iframe_html = f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            title="{title}"
            width="{iframe_width}"
            height="{iframe_height}"
            style="border: none;"
            loading="lazy"
        ></iframe>
    """

    components.html(iframe_html, height=(iframe_height if isinstance(iframe_height, int) else 600))
