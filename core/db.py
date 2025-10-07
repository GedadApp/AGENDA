import streamlit as st
import psycopg, psycopg.rows

class Db:
    def __init__(self):
        pass

    @st.cache_resource(show_spinner=False)
    def get_conn(_self):
        cfg = st.secrets.get("db", {})
        conn = psycopg.connect(
            host=cfg.get("host", "localhost"),
            port=cfg.get("port", 5432),
            dbname=cfg.get("dbname", "postgres"),
            user=cfg.get("user", "postgres"),
            password=cfg.get("password", "postgres"),
            row_factory=psycopg.rows.dict_row,
        )
        return conn

    def qall(self, sql, params=None):
        with self.get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchall()

    def qone(self, sql, params=None):
        with self.get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchone()

    def qexec(self, sql, params=None):
        with self.get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql, params or [])
            conn.commit()
            return cur.rowcount

    # Schemas "injetados" conforme seu app atual
    def ensure_schema_agenda(self):
        self.qexec("create extension if not exists pgcrypto;")
        self.qexec("""
        create table if not exists agenda (
          id uuid primary key default gen_random_uuid(),
          entidade    text not null,
          data        date not null,
          indice      smallint not null check (indice between 1 and 12),
          inicio      smallint,
          consulente  text not null,
          primeiravez text,
          observacao  text,
          status      text not null check (status in ('AGENDADO','AGUARDANDO','FINALIZADO')),
          telefone    text not null,
          criadopor   text not null,
          criadoem    timestamptz not null default now(),
          constraint agenda_unique_idx unique (entidade, data, indice)
        );
        """)

    def ensure_schema_reiki_series(self):
        self.qexec("create extension if not exists pgcrypto;")
        self.qexec("""
        create table if not exists reiki_cromo_agenda (
          "ID" uuid primary key default gen_random_uuid(),
          "DATA_CONSULTA" date not null,
          "ENTIDADE"      text not null,
          "INDICE"        smallint not null check ("INDICE" between 1 and 12),
          "CHEGADA"       smallint,
          "NOME"          text not null,
          "STATUS"        text not null,
          "TELEFONE"      text,
          "DATA1"         date not null,
          "DATA2"         date,
          "DATA3"         date,
          "OBSERVAÇÃO"    text,
          "CRIADOEM"      timestamptz not null default now(),
          "CRIADOPOR"     text not null,
          "TERAPIA"       text not null default 'REIKI'
        );
        """)
        # Drop antigos constraints de terça se existirem (mantendo lógica no serviço)
        try:
            self.qexec('ALTER TABLE reiki_cromo_agenda DROP CONSTRAINT IF EXISTS rca_tuesday_data;')
            self.qexec('ALTER TABLE reiki_cromo_agenda DROP CONSTRAINT IF EXISTS rca_tuesday_d1;')
            self.qexec('ALTER TABLE reiki_cromo_agenda DROP CONSTRAINT IF EXISTS rca_tuesday_d2;')
            self.qexec('ALTER TABLE reiki_cromo_agenda DROP CONSTRAINT IF EXISTS rca_tuesday_d3;')
        except Exception:
            pass

    def ensure_auth_schema(self):
        self.qexec("create extension if not exists pgcrypto;")
        self.qexec("""
        CREATE UNIQUE INDEX IF NOT EXISTS users_email_ci_unique ON users (lower(email));
        """)
        self.qexec("""
        ALTER TABLE users
          ADD COLUMN IF NOT EXISTS password_hash       text,
          ADD COLUMN IF NOT EXISTS password_updated_at timestamptz,
          ADD COLUMN IF NOT EXISTS failed_logins       integer NOT NULL DEFAULT 0,
          ADD COLUMN IF NOT EXISTS locked_until        timestamptz;
        """)
