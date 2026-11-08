import sqlite3
import pandas as pd
from processor import SkillExtractor


class JobDatabase:
#Inicializacion de la base de datos
  def __init__(self, db_name="empleos.db"):
    self.db_name = db_name
    self.init_db()
#Conexion a SQLite
  def get_connection(self):
    return sqlite3.connect(self.db_name)
#Crear la tabla de vacantes si no existe
  def init_db(self):
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacantes (
                id_vacante TEXT PRIMARY KEY,
                titulo TEXT,
                empresa TEXT,
                ubicacion TEXT,
                modalidad TEXT,
                salario_promedio_usd INTEGER,
                url_vacante TEXT,
                descripcion_raw TEXT,
                habilidades_requeridas TEXT
            )
            """)
      conn.commit()

  def save_vacancies(self, df):
    """Guarda o actualiza las vacantes en SQLite sanitizando tipos de datos no compatibles."""
    df_to_save = df.copy()

    # Convertir diccionarios o listas a cadenas de texto plano para evitar errores en SQLite
    for col in df_to_save.columns:
      df_to_save[col] = df_to_save[col].apply(
          lambda x: (
              ", ".join(map(str, x))
              if isinstance(x, list)
              else (
                  str(x.get("name", x))
                  if isinstance(x, dict)
                  else (str(x) if pd.notnull(x) else "")
              )
          )
      )

    with self.get_connection() as conn:
      df_to_save.to_sql("vacantes", conn, if_exists="replace", index=False)
#Leer todas las vacantes de la base de datos y convertir habilidades requeridas a listas
  def get_all_vacancies(self):
    with self.get_connection() as conn:
      df = pd.read_sql("SELECT * FROM vacantes", conn)
      if not df.empty and "habilidades_requeridas" in df.columns:
        df["habilidades_requeridas"] = df["habilidades_requeridas"].apply(
            lambda x: (
                [s.strip() for s in x.split(",")]
                if isinstance(x, str) and x
                else []
            )
        )
      return df
#Analisis de demanda de habilidades
  def analyze_user_skills_demand(self, user_skills):
    df = self.get_all_vacancies()
    if df.empty or not user_skills:
      return pd.DataFrame()

    results = []
    user_skills_clean = [s.lower().strip() for s in user_skills if s.strip()]
#Match de habilidades del usuario con las vacantes
    for skill in user_skills_clean:
      matches = df[
          df.apply(
              lambda row: skill
              in [s.lower() for s in row["habilidades_requeridas"]]
              or SkillExtractor.is_skill_in_text(skill, row["descripcion_raw"]),
              axis=1,
          )
      ]
      total_matches = len(matches)

      # Convertir salario a entero/flotante numérico seguro
      salarios = pd.to_numeric(
          matches["salario_promedio_usd"], errors="coerce"
      ).fillna(0)
      avg_salary = salarios.mean() if total_matches > 0 else 0

      results.append({
          "habilidad": skill,
          "total_vacantes_que_la_piden": total_matches,
          "salario_promedio_ofertas": round(avg_salary, 2),
      })

    res_df = pd.DataFrame(results)
    return res_df.sort_values(
        by=["total_vacantes_que_la_piden", "salario_promedio_ofertas"],
        ascending=False,
    )
#Calculo del porcentaje de match
  def calculate_match_score(self, user_skills):
    df = self.get_all_vacancies()
    if df.empty or not user_skills:
      return pd.DataFrame()

    user_skills_clean = [s.lower().strip() for s in user_skills if s.strip()]

    def compute_match(row):
      matched_skills = set()
      desc = row.get("descripcion_raw", "")
      req_skills = set([s.lower() for s in row["habilidades_requeridas"]])

      for skill in user_skills_clean:
        if skill in req_skills or SkillExtractor.is_skill_in_text(skill, desc):
          matched_skills.add(skill)

      matches_count = len(matched_skills)
      total_req = len(user_skills_clean)
      match_pct = (
          round((matches_count / total_req) * 100, 2) if total_req > 0 else 0.0
      )

      return pd.Series([matches_count, total_req, match_pct])

    df[
        [
            "habilidades_coincidentes",
            "total_habilidades_evaluadas",
            "porcentaje_match",
        ]
    ] = df.apply(compute_match, axis=1)

    # Convertir columna de salario para evitar problemas de ordenamiento
    df["salario_promedio_usd"] = pd.to_numeric(
        df["salario_promedio_usd"], errors="coerce"
    ).fillna(0)

    filtered = df[df["habilidades_coincidentes"] > 0]
    return filtered.sort_values(
        by=["porcentaje_match", "habilidades_coincidentes"], ascending=False
    )