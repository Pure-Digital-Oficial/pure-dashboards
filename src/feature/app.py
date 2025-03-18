import streamlit as st
from feature.pages.time_notes_dashboard import TimeNotesDashboard

class App:
    def __init__(self):
        st.set_page_config(page_title="Analises Pure Digital", layout="wide")
        self.pages = {
            "Página Principal": self.render_main_page,
            "Apontamentos Dashboard": TimeNotesDashboard().render_page
        }

    def render_main_page(self):
        st.title('DASHBOARDS PURE DIGITAL :rocket:')
        st.write("Escolha uma página no menu lateral.")
    
    def run(self):
        page = st.sidebar.selectbox("Escolha a página", list(self.pages.keys()))
        self.pages[page]()
