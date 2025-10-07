from datetime import date, timedelta, datetime
from typing import Optional, Dict, Any, List
from data.repos import UsersRepo, AgendaRepo, ReikiCromoRepo

class AuthService:
    def __init__(self, db):
        self.db = db
        self.users = UsersRepo(db)

    def login(self, email: str, password: str) -> Optional[dict]:
        lock = self.users.get_lock_and_active(email)
        if not lock or not lock.get('ativo', True):
            return None
        if lock.get('locked_until') and lock['locked_until'] > datetime.utcnow():
            return None
        user = self.users.validate_password(email, password)
        if not user:
            self.users.inc_failed_login(email)
            return None
        self.users.reset_failed_login(email)
        return {
            "email": user['email'],
            "nome": user.get('nome',''),
            "perfil": user.get('perfil','user'),
            "entidade": user.get('entidade','')
        }

class AgendaService:
    def __init__(self, db):
        self.db = db
        self.repo = AgendaRepo(db)

    def list(self, dt: Optional[str], entidade: Optional[str]):
        return self.repo.list(dt, entidade)

    def save(self, row: Dict[str, Any], row_id: Optional[str]=None):
        # Duplicate check when updating
        if row_id:
            if self.repo.exists_other_same_slot(row['entidade'], row['data'], row['indice'], row_id):
                raise ValueError("Já existe agendamento para esta entidade/data/índice.")
            return self.repo.update(row_id, row)
        else:
            if self.repo.exists_other_same_slot(row['entidade'], row['data'], row['indice'], None):
                raise ValueError("Já existe agendamento para esta entidade/data/índice.")
            res = self.repo.insert(row)
            return res['id'] if res else None

    def delete(self, row_id: str):
        return self.repo.delete(row_id)


def is_tuesday(d: date) -> bool:
    return d.weekday() == 1

def next_tuesday_after(d: date) -> date:
    days = (1 - d.weekday()) % 7
    return d + timedelta(days=days if days else 7)

def generate_series_dates(start_date: date):
    if not is_tuesday(start_date):
        start_date = next_tuesday_after(start_date)
    d1 = start_date
    d2 = next_tuesday_after(d1)
    d3 = next_tuesday_after(d2)
    return d1, d2, d3

class ReikiService:
    def __init__(self, db):
        self.db = db
        self.repo = ReikiCromoRepo(db)

    def list(self, dt: Optional[str], entidade: Optional[str]):
        return self.repo.list(dt, entidade)

    def create_series(self, entidade: str, indice: int, nome: str, status: str,
                      telefone: Optional[str], data_consulta: date, observacao: Optional[str],
                      terapia: str, criadopor: str):
        d1, d2, d3 = generate_series_dates(data_consulta)
        row = {
            "entidade": entidade,
            "indice": indice,
            "nome": nome,
            "status": status,
            "telefone": telefone,
            "data_consulta": data_consulta,
            "data1": d1, "data2": d2, "data3": d3,
            "observacao": observacao,
            "terapia": terapia,
            "criadopor": criadopor,
        }
        # Verificar conflito
        if self.repo.exists_other_same_slot(entidade, str(data_consulta), indice, None):
            raise ValueError("Conflito: Já existe série para ENTIDADE/DATA/ÍNDICE.")
        res = self.repo.insert_series(row)
        return res['ID'] if res else None

    def update(self, row_id: str, row: Dict[str, Any]):
        # Verificar conflitos por índice/chegada quando atualiza
        if self.repo.exists_other_same_slot(row['entidade'], row['data_consulta'], row['indice'], row_id):
            raise ValueError("Conflito: ENTIDADE/DATA/ÍNDICE já utilizado.")
        if row.get('chegada') is not None:
            if self.repo.exists_other_same_chegada(row['entidade'], row['data_consulta'], row['chegada'], row_id):
                raise ValueError("Conflito: Chegada já utilizada para esta ENTIDADE/DATA.")
        return self.repo.update(row_id, row)

    def delete(self, row_id: str):
        return self.repo.delete(row_id)


class ReportService:
    def __init__(self, db):
        self.db = db

    def resumo_agenda(self, dt: str):
        return self.db.qall("""SELECT entidade,
       COUNT(*) as total,
       COUNT(*) FILTER (WHERE status='AGENDADO')   as agendado,
       COUNT(*) FILTER (WHERE status='AGUARDANDO') as aguardando,
       COUNT(*) FILTER (WHERE status='FINALIZADO') as finalizado
  FROM agenda
 WHERE data=%s
 GROUP BY entidade
 ORDER BY entidade
        """, [dt])

    def resumo_terapias(self):
        # Repassa para o repo do Reiki por simplicidade
        from data.repos import ReikiCromoRepo
        return ReikiCromoRepo(self.db).resumo_terapia()
