import streamlit as st

class AgendaPage:
    def __init__(self, db, auth_service, agenda_service):
        self.db = db
        self.auth = auth_service
        self.agenda = agenda_service

    def render(self, user):
        st.markdown('<div class="modern-card"><div class="legend">Filtros</div></div>', unsafe_allow_html=True)
        with st.expander("Filtros de busca", expanded=True):
            c1,c2,c3 = st.columns([1.2,1.2,1])
            dt = c1.date_input("Data")
            ent = c2.text_input("Entidade")
            buscar = c3.button("Buscar", use_container_width=True)
            if buscar:
                st.session_state['agenda_rows'] = self.agenda.list(dt=str(dt) if dt else None, entidade=ent or None)

        rows = st.session_state.get('agenda_rows', [])
        st.markdown('<div class="modern-card"><div class="legend">Agenda do dia <span class="pill">Resultados</span></div></div>', unsafe_allow_html=True)
        st.dataframe(rows, use_container_width=True)
        st.caption("Dica: clique no cabeçalho para ordenar por índice.")

        st.markdown('<div class="modern-card"><div class="legend">Novo / Editar</div></div>', unsafe_allow_html=True)
        with st.form("agenda_form", clear_on_submit=True):
            c1,c2,c3 = st.columns([1,1,1])
            entidade = c1.text_input("Entidade")
            data = c2.date_input("Data")
            indice = c3.number_input("Índice (1–12)", min_value=1, max_value=12, step=1)

            c4,c5,c6 = st.columns([1,2,1])
            inicio = c4.number_input("Início (min)", min_value=0, step=5)
            consulente = c5.text_input("Consulente")
            telefone = c6.text_input("Telefone")

            c7,c8 = st.columns([1,1])
            primeiravez = c7.text_input("Primeira vez?")
            status = c8.selectbox("Status", ["AGENDADO","AGUARDANDO","FINALIZADO"])

            observacao = st.text_area("Observação")
            row_id = st.text_input("ID (preencha para atualizar; deixe vazio para criar)")

            btn = st.form_submit_button("Salvar", use_container_width=True)
            if btn:
                try:
                    row = {
                        "entidade": entidade, "data": str(data), "indice": int(indice),
                        "inicio": int(inicio), "consulente": consulente, "primeiravez": primeiravez,
                        "observacao": observacao, "status": status, "telefone": telefone,
                        "criadopor": user.get("email","")
                    }
                    if row_id.strip():
                        self.agenda.save(row, row_id=row_id.strip())
                        st.success("Registro atualizado com sucesso.")
                    else:
                        new_id = self.agenda.save(row, row_id=None)
                        st.success(f"Registro criado. ID: {new_id}")
                    st.session_state['agenda_rows'] = self.agenda.list(dt=str(data), entidade=entidade)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.markdown('<div class="modern-card"><div class="legend">Excluir</div></div>', unsafe_allow_html=True)
        cdel1, cdel2 = st.columns([2,1])
        del_id = cdel1.text_input("ID para excluir")
        if cdel2.button("Excluir", use_container_width=True):
            if del_id.strip():
                self.agenda.delete(del_id.strip())
                st.success("Excluído.")
            else:
                st.warning("Informe um ID.")
