import streamlit as st
from feature.pages.timekepping_dashboard import TimekeppingDashboard

class App:
    def __init__(self):
        st.set_page_config(page_title="Analises Pure Digital", layout="wide")
        self.pages = {
            "Página Principal": self.render_main_page,
            "Timekeeping Dashboard": TimekeppingDashboard().renderPage
        }

    def render_main_page(self):
        st.title('DASHBOARDS PURE DIGITAL :rocket:')
        st.write("Escolha uma página no menu lateral.")
    
    def run(self):
        page = st.sidebar.selectbox("Escolha a página", list(self.pages.keys()))
        self.pages[page]()
