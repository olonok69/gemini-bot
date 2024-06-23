import streamlit as st

st.markdown(
    """
    <style>
    .stTextArea [data-baseweb=base-input] {
        background-image: linear-gradient(140deg, rgb(54, 36, 31) 0%, rgb(121, 56, 100) 50%, rgb(106, 117, 25) 75%);
        -webkit-text-fill-color: white;
    }

    .stTextArea [data-baseweb=base-input] [disabled=""]{
        background-image: linear-gradient(45deg, red, purple, red);
        -webkit-text-fill-color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

disable_textarea = st.checkbox("Disable text area:")

st.text_area(
    label="Text area:",
    value="This is a repeated sentence " * 20,
    height=300,
    disabled=disable_textarea,
)
