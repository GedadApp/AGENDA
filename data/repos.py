from typing import Optional, Dict, Any, List

class UsersRepo:
    def __init__(self, db):
        self.db = db

    def get_lock_and_active(self, email: str):
        return self.db.qone("""SELECT locked_until, coalesce(ativo,true) AS ativo
  FROM users
 WHERE lower(email)=lower(%s)
        """, [email])

    def validate_password(self, email: str, password: str):
        return self.db.qone("""SELECT email, entidade, perfil, nome, coalesce(ativo,true) AS ativo
  FROM users
 WHERE lower(email) = lower(%s)
   AND password_hash IS NOT NULL
   AND password_hash = crypt(%s, password_hash)
        """, [email, password])

    def inc_failed_login(self, email: str):
        return self.db.qexec("""UPDATE users
   SET failed_logins = failed_logins + 1,
       locked_until  = CASE
                         WHEN failed_logins >= 4 THEN now() + interval '15 minutes'
                         ELSE locked_until
                       END
 WHERE lower(email) = lower(%s)
        """, [email])

    def reset_failed_login(self, email: str):
        return self.db.qexec("""UPDATE users
   SET failed_logins=0, locked_until=NULL
 WHERE lower(email)=lower(%s)
        """, [email])

    def set_password(self, email: str, new_password: str):
        return self.db.qexec("""UPDATE users
   SET password_hash = crypt(%s, gen_salt('bf', 12)),
       password_updated_at = now(),
       failed_logins = 0,
       locked_until = NULL
 WHERE lower(email)=lower(%s)
        """, [new_password, email])

    def clear_password(self, email: str):
        return self.db.qexec("""UPDATE users
   SET password_hash = NULL,
       password_updated_at = now(),
       failed_logins = 0,
       locked_until = NULL
 WHERE lower(email)=lower(%s)
        """, [email])


class AgendaRepo:
    def __init__(self, db):
        self.db = db

    def list(self, dt: Optional[str]=None, entidade: Optional[str]=None):
        sql = """select id, entidade, to_char(data,'YYYY-MM-DD') as data, indice,
       inicio, consulente, primeiravez, observacao, status, telefone,
       criadopor, to_char(criadoem at time zone 'America/Sao_Paulo','YYYY-MM-DD HH24:MI') as criadoem
  from agenda
 where (%s is null or data=%s)
   and (%s is null or entidade=%s)
 order by data, entidade, indice
        """
        return self.db.qall(sql, [dt, dt, entidade, entidade])

    def get(self, row_id: str):
        return self.db.qone("""select id, entidade, data::text as data, indice, inicio, consulente,
       primeiravez, observacao, status, telefone
  from agenda where id=%s
        """, [row_id])

    def exists_other_same_slot(self, entidade: str, data: str, indice: int, exclude_id: Optional[str]):
        return self.db.qone("""select 1 from agenda
 where entidade=%s and data=%s and indice=%s and id<>%s limit 1
        """, [entidade, data, indice, exclude_id or '00000000-0000-0000-0000-000000000000'])

    def insert(self, row: Dict[str, Any]):
        return self.db.qone("""INSERT INTO agenda (entidade, data, indice, inicio, consulente,
                    primeiravez, observacao, status, telefone, criadopor)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
RETURNING id
        """, [
            row['entidade'], row['data'], row['indice'], row.get('inicio'),
            row['consulente'], row.get('primeiravez'), row.get('observacao'),
            row['status'], row['telefone'], row['criadopor']
        ])

    def update(self, row_id: str, row: Dict[str, Any]):
        return self.db.qexec("""update agenda
   set entidade=%s, data=%s, indice=%s, inicio=%s,
       consulente=%s, primeiravez=%s, observacao=%s,
       status=%s, telefone=%s
 where id=%s
        """, [
            row['entidade'], row['data'], row['indice'], row.get('inicio'),
            row['consulente'], row.get('primeiravez'), row.get('observacao'),
            row['status'], row['telefone'], row_id
        ])

    def delete(self, row_id: str):
        return self.db.qexec("delete from agenda where id=%s", [row_id])


class ReikiCromoRepo:
    def __init__(self, db):
        self.db = db

    def list(self, dt: Optional[str]=None, entidade: Optional[str]=None):
        sql = """select "ID","ENTIDADE", to_char("DATA_CONSULTA",'YYYY-MM-DD') as data_consulta,
       "INDICE","CHEGADA","NOME","STATUS","TELEFONE",
       to_char("DATA1",'YYYY-MM-DD') as data1,
       to_char("DATA2",'YYYY-MM-DD') as data2,
       to_char("DATA3",'YYYY-MM-DD') as data3,
       "OBSERVAÇÃO", to_char("CRIADOEM" at time zone 'America/Sao_Paulo','YYYY-MM-DD HH24:MI') as criadoem,
       "CRIADOPOR","TERAPIA"
  from reiki_cromo_agenda
 where (%s is null or "DATA_CONSULTA"=%s)
   and (%s is null or "ENTIDADE"=%s)
 order by "DATA_CONSULTA","ENTIDADE","INDICE"
        """
        return self.db.qall(sql, [dt, dt, entidade, entidade])

    def get(self, row_id: str):
        return self.db.qone("""select "ID","ENTIDADE","DATA_CONSULTA"::text as data_consulta,"INDICE","CHEGADA",
       "NOME","STATUS","TELEFONE",
       "DATA1"::text as data1,"DATA2"::text as data2,"DATA3"::text as data3,"OBSERVAÇÃO","TERAPIA"
  from reiki_cromo_agenda where "ID"=%s
        """, [row_id])

    def exists_other_same_slot(self, entidade: str, data_consulta: str, indice: int, exclude_id: Optional[str]):
        return self.db.qone("""select 1 from reiki_cromo_agenda
 where "ENTIDADE"=%s and "DATA_CONSULTA"=%s and "INDICE"=%s and "ID"<>%s limit 1
        """, [entidade, data_consulta, indice, exclude_id or '00000000-0000-0000-0000-000000000000'])

    def exists_other_same_chegada(self, entidade: str, data_consulta: str, chegada: int, exclude_id: Optional[str]):
        return self.db.qone("""select 1 from reiki_cromo_agenda
 where "ENTIDADE"=%s and "DATA_CONSULTA"=%s and "CHEGADA"=%s and "ID"<>%s limit 1
        """, [entidade, data_consulta, chegada, exclude_id or '00000000-0000-0000-0000-000000000000'])

    def insert_series(self, row: Dict[str, Any]):
        return self.db.qone("""insert into reiki_cromo_agenda
  ("DATA_CONSULTA","ENTIDADE","INDICE","NOME","STATUS","TELEFONE",
   "DATA1","DATA2","DATA3","OBSERVAÇÃO","TERAPIA","CRIADOPOR")
values
  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
returning "ID"
        """, [
            row['data_consulta'], row['entidade'], row['indice'], row['nome'],
            row['status'], row.get('telefone'),
            row['data1'], row.get('data2'), row.get('data3'),
            row.get('observacao'), row.get('terapia','REIKI'), row['criadopor']
        ])

    def update(self, row_id: str, row: Dict[str, Any]):
        return self.db.qexec("""update reiki_cromo_agenda
   set "ENTIDADE"=%s, "DATA_CONSULTA"=%s, "INDICE"=%s, "CHEGADA"=%s,
       "NOME"=%s, "STATUS"=%s, "TELEFONE"=%s,
       "DATA1"=%s, "DATA2"=%s, "DATA3"=%s,
       "OBSERVAÇÃO"=%s, "TERAPIA"=%s
 where "ID"=%s
        """, [
            row['entidade'], row['data_consulta'], row['indice'], row.get('chegada'),
            row['nome'], row['status'], row.get('telefone'),
            row['data1'], row.get('data2'), row.get('data3'),
            row.get('observacao'), row.get('terapia','REIKI'), row_id
        ])

    def delete(self, row_id: str):
        return self.db.qexec('delete from reiki_cromo_agenda where "ID"=%s', [row_id])

    def resumo_terapia(self):
        return self.db.qall("""SELECT "TERAPIA", "ENTIDADE",
       COUNT(*) as total,
       SUM(CASE WHEN "STATUS"='AGENDADO'  THEN 1 ELSE 0 END) as agendado,
       SUM(CASE WHEN "STATUS"='AGUARDANDO' THEN 1 ELSE 0 END) as aguardando,
       SUM(CASE WHEN "STATUS"='FINALIZADO' THEN 1 ELSE 0 END) as finalizado
  FROM reiki_cromo_agenda
 GROUP BY "TERAPIA","ENTIDADE"
 ORDER BY "TERAPIA","ENTIDADE"
        """)
