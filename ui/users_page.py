import streamlit as st

class UsersAdminPage:
    def __init__(self, db, auth_service):
        self.db = db
        self.auth = auth_service

    def render(self, user):
        st.markdown('<div class="modern-card"><div class="legend">Administração de Usuários</div></div>', unsafe_allow_html=True)
        st.info("Implantar listagem e edição conforme sua regra atual (perfis, bloqueios, reset de senha, etc.).")
