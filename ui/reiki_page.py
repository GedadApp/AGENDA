import streamlit as st
from datetime import date

class ReikiPage:
    def __init__(self, db, auth_service, reiki_service):
        self.db = db
        self.auth = auth_service
        self.reiki = reiki_service

    def render(self, user):
        st.markdown('<div class="modern-card"><div class="legend">Filtros</div></div>', unsafe_allow_html=True)
        with st.expander("Filtros de séries", expanded=True):
            c1,c2,c3 = st.columns([1.2,1.2,1])
            dt = c1.date_input("Data da consulta")
            ent = c2.text_input("Entidade")
            buscar = c3.button("Buscar séries", use_container_width=True)
            if buscar:
                st.session_state['reiki_rows'] = self.reiki.list(dt=str(dt) if dt else None, entidade=ent or None)

        rows = st.session_state.get('reiki_rows', [])
        st.markdown('<div class="modern-card"><div class="legend">Séries <span class="pill">Resultados</span></div></div>', unsafe_allow_html=True)
        st.dataframe(rows, use_container_width=True)

        st.markdown('<div class="modern-card"><div class="legend">Criar Série (D1/D2/D3 automáticos)</div></div>', unsafe_allow_html=True)
        with st.form("reiki_form", clear_on_submit=True):
            c1,c2,c3 = st.columns([1,1,1])
            entidade = c1.text_input("Entidade")
            data_consulta = c2.date_input("Data da consulta", value=date.today())
            indice = c3.number_input("Índice (1–12)", min_value=1, max_value=12, step=1)

            c4,c5 = st.columns([2,1])
            nome = c4.text_input("Nome")
            status = c5.selectbox("Status", ["AGENDADO","AGUARDANDO","FINALIZADO"])

            c6,c7 = st.columns([1,1])
            telefone = c6.text_input("Telefone")
            terapia = c7.selectbox("Terapia", ["REIKI","CROMO"])

            observacao = st.text_area("Observação")

            submit = st.form_submit_button("Criar Série", use_container_width=True)
            if submit:
                try:
                    new_id = self.reiki.create_series(
                        entidade=entidade, indice=int(indice), nome=nome, status=status,
                        telefone=telefone, data_consulta=data_consulta, observacao=observacao,
                        terapia=terapia, criadopor=user.get("email","")
                    )
                    st.success(f"Série criada. ID: {new_id}")
                    st.session_state['reiki_rows'] = self.reiki.list(dt=str(data_consulta), entidade=entidade)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.markdown('<div class="modern-card"><div class="legend">Atualizar / Excluir</div></div>', unsafe_allow_html=True)
        up_id = st.text_input("ID para atualizar")
        if up_id:
            with st.form("reiki_update", clear_on_submit=False):
                c1,c2,c3,c4 = st.columns([1,1,1,1])
                entidade = c1.text_input("Entidade")
                data_consulta = c2.text_input("Data consulta (YYYY-MM-DD)")
                indice = c3.number_input("Índice", min_value=1, max_value=12, step=1)
                chegada = c4.number_input("Chegada (opcional)", min_value=0, step=1)
                nome = st.text_input("Nome")
                status = st.selectbox("Status", ["AGENDADO","AGUARDANDO","FINALIZADO"])
                telefone = st.text_input("Telefone")
                data1 = st.text_input("DATA1 (YYYY-MM-DD)")
                data2 = st.text_input("DATA2 (YYYY-MM-DD)")
                data3 = st.text_input("DATA3 (YYYY-MM-DD)")
                observacao = st.text_area("Observação")
                terapia = st.selectbox("Terapia", ["REIKI","CROMO"], key="terapia_update")
                if st.form_submit_button("Salvar atualização", use_container_width=True):
                    row = {
                        "entidade": entidade, "data_consulta": data_consulta, "indice": int(indice),
                        "chegada": int(chegada) if chegada else None, "nome": nome, "status": status,
                        "telefone": telefone, "data1": data1, "data2": data2 or None, "data3": data3 or None,
                        "observacao": observacao, "terapia": terapia
                    }
                    try:
                        self.reiki.update(up_id.strip(), row)
                        st.success("Atualizado.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        cdel1, cdel2 = st.columns([2,1])
        del_id = cdel1.text_input("ID para excluir")
        if cdel2.button("Excluir série", use_container_width=True):
            if del_id.strip():
                self.reiki.delete(del_id.strip())
                st.success("Excluída.")
            else:
                st.warning("Informe um ID.")
