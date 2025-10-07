import streamlit as st

from core.db import Db
from core.theme import inject_modern_css
from domain.services import AuthService, AgendaService, ReikiService, ReportService
from ui.agenda_page import AgendaPage
from ui.reiki_page import ReikiPage
from ui.reports_page import ReportsPage
from ui.users_page import UsersAdminPage

st.set_page_config(page_title="Agenda GEDAD", layout="wide", initial_sidebar_state="collapsed")

inject_modern_css(st)

db = Db()
auth = AuthService(db=db)
agenda_service = AgendaService(db=db)
reiki_service = ReikiService(db=db)
report_service = ReportService(db=db)

db.ensure_auth_schema()
db.ensure_schema_agenda()
db.ensure_schema_reiki_series()

if "user" not in st.session_state:
    st.session_state["user"] = None

def _login_form():
    st.markdown('<div class="modern-header"><h2>Agenda GEDAD — Login</h2><div class="muted">Acesse com seu e-mail e senha</div></div>', unsafe_allow_html=True)
    with st.container():
        c1,c2 = st.columns([1,1])
        email = c1.text_input("Email")
        senha = c2.text_input("Senha", type="password")
        if st.button("Entrar", use_container_width=True):
            user = auth.login(email=email, password=senha)
            if user:
                st.session_state["user"] = user
                st.success("Login realizado.")
                st.rerun()
            else:
                st.error("Credenciais inválidas ou usuário bloqueado.")

def _sidebar(user):
    with st.sidebar:
        st.image("https://dummyimage.com/300x100/eee/444.png&text=GEDAD", use_container_width=True)
        st.caption(f"Usuário: **{user.get('nome','')}**  |  Perfil: **{user.get('perfil','')}**")
        page = st.radio("Navegação", ["AGENDA", "REIKI", "RELATORIOS", "USERS"], key="nav_radio")
        if st.button("Sair", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()
    return page

def main():
    user = st.session_state["user"]
    if not user:
        _login_form()
        return

    st.markdown('<div class="modern-header"><h2>Agenda GEDAD</h2><div class="muted">Sistema de agendamentos e terapias</div></div>', unsafe_allow_html=True)
    page = _sidebar(user)

    if page == "AGENDA":
        AgendaPage(db=db, auth_service=auth, agenda_service=agenda_service).render(user=user)
    elif page == "REIKI":
        ReikiPage(db=db, auth_service=auth, reiki_service=reiki_service).render(user=user)
    elif page == "RELATORIOS":
        ReportsPage(db=db, auth_service=auth, report_service=report_service).render(user=user)
    elif page == "USERS":
        UsersAdminPage(db=db, auth_service=auth).render(user=user)

if __name__ == "__main__":
    main()
