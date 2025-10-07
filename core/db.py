import os
import streamlit as st
import psycopg, psycopg.rows

FRIENDLY_MISSING_SECRETS = """
❌ Não foi possível conectar ao banco.

Configure os segredos do Streamlit com suas credenciais do Supabase:

[db]
# Opção 1 (recomendada): URL completa (pooling 6543)
url = "postgresql://USER:PASSWORD@HOST:6543/postgres?sslmode=require"

# Opção 2: campos separados
host = "HOST.supabase.co"         # ou aws-0-...pooler.supabase.com
port = 6543                       # pooling = 6543  |  direct = 5432
dbname = "postgres"
user = "postgres.xxxxx"
password = "SUA-SENHA"
sslmode = "require"
"""

class Db:
    def __init__(self):
        pass

    @st.cache_resource(show_spinner=False)
    def get_conn(_self):
        # Prefer DATABASE_URL env, then st.secrets["db"]["url"], else discrete fields
        env_url = os.getenv("DATABASE_URL")
        cfg = st.secrets.get("db", {})
        url = env_url or cfg.get("url")

        try:
            if url:
                # Ensure sslmode=require if not present
                if "sslmode" not in url:
                    url = (url + ("&" if "?" in url else "?") + "sslmode=require")
                conn = psycopg.connect(url, row_factory=psycopg.rows.dict_row)
            else:
                host = cfg.get("host")
                port = int(cfg.get("port", 0)) if cfg.get("port") else None
                dbname = cfg.get("dbname")
                user = cfg.get("user")
                password = cfg.get("password")
                sslmode = cfg.get("sslmode", "require")

                # Friendly guard
                if not all([host, port, dbname, user, password]):
                    st.error(FRIENDLY_MISSING_SECRETS)
                    st.stop()

                conn = psycopg.connect(
                    host=host, port=port, dbname=dbname, user=user, password=password,
                    row_factory=psycopg.rows.dict_row, sslmode=sslmode
                )
        except Exception as e:
            st.error(FRIENDLY_MISSING_SECRETS)
            st.exception(e)
            st.stop()

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

    # ---------- Schemas ----------
    def ensure_schema_agenda(self):
        # pgcrypto pode já estar habilitado no Supabase. Ignorar erros.
        try:
            self.qexec("create extension if not exists pgcrypto;")
        except Exception:
            pass

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
        try:
            self.qexec("create extension if not exists pgcrypto;")
        except Exception:
            pass

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
        # Remover constraints antigas opcionais (sem falhar)
        for c in ('rca_tuesday_data','rca_tuesday_d1','rca_tuesday_d2','rca_tuesday_d3'):
            try:
                self.qexec(f'ALTER TABLE reiki_cromo_agenda DROP CONSTRAINT IF EXISTS {c};')
            except Exception:
                pass

    def ensure_auth_schema(self):
        try:
            self.qexec("create extension if not exists pgcrypto;")
        except Exception:
            pass

        # Garantir tabela users antes de índice/alter
        self.qexec("""
        create table if not exists users (
            id bigserial primary key,
            email text unique not null,
            nome  text,
            entidade text,
            perfil text default 'user',
            ativo boolean default true,
            password_hash text,
            password_updated_at timestamptz,
            failed_logins integer not null default 0,
            locked_until timestamptz
        );
        """ )

        # Índice de e-mail case-insensitive
        try:
            self.qexec("""
            CREATE UNIQUE INDEX IF NOT EXISTS users_email_ci_unique ON users (lower(email));
            """)
        except Exception:
            pass
