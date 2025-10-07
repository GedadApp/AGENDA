import streamlit as st

class ReportsPage:
    def __init__(self, db, auth_service, report_service):
        self.db = db
        self.auth = auth_service
        self.reports = report_service

    def render(self, user):
        st.markdown('<div class="modern-card"><div class="legend">Relatórios</div></div>', unsafe_allow_html=True)
        dt = st.date_input("Data do resumo (Agenda)")
        if st.button("Gerar resumo Agenda", use_container_width=True):
            rows = self.reports.resumo_agenda(str(dt))
            st.dataframe(rows, use_container_width=True)
        st.markdown('<div class="modern-card"><div class="legend">Resumo Terapias</div></div>', unsafe_allow_html=True)
        if st.button("Gerar resumo Terapias", use_container_width=True):
            rows = self.reports.resumo_terapias()
            st.dataframe(rows, use_container_width=True)
