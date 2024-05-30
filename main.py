from __future__ import annotations
import streamlit as st
from mindmap import MindMap
from utils import START_CONVERSATION, ask_chatgpt, Message

st.set_page_config(page_title="SmartEd Connect loyihasi", layout="wide")

def main():
    mindmap = MindMap.load()

    st.sidebar.title("SmartEDU generatori")

    graph_type = st.sidebar.radio("Grafning ko'rinish turini tanlang", options=["graf", "tarmoqli"])

    empty = mindmap.is_empty()
    reset = empty or st.sidebar.checkbox("Qayta tiklash", value=False)
    query = st.sidebar.text_area(
        "Grafikni tasvirlab bering" if reset else "Grafikni qanday o'zgartirishni tasvirlab bering", 
        value=st.session_state.get("mindmap-input", ""),
        key="mindmap-input",
        height=200
    )
    submit = st.sidebar.button("Yaratish")

    valid_submission = submit and query != ""

    if empty and not valid_submission:
        return
    
    with st.spinner(text="Graf yaratilmoqda..."):
        if valid_submission:
            if reset:
                mindmap.ask_for_initial_graph(query=query)
            else:
                mindmap.ask_for_extended_graph(text=query)
            st.rerun()
        else:
            mindmap.visualize(graph_type)

if __name__ == "__main__":
    main()
