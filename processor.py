import re
import pandas as pd


class SkillExtractor:
#Diccionario de habilidades
  def __init__(self):
    self.skills_catalog = {
        "python": r"\bpython\b",
        "sql": r"\bsql\b",
        "bigquery": r"\b(bigquery|google bigquery)\b",
        "docker": r"\bdocker\b",
        "git": r"\bgit\b",
        "power bi": r"\b(power bi|powerbi)\b",
        "tableau": r"\btableau\b",
        "excel": r"\bexcel\b",
        "aws": r"\b(aws|amazon web services)\b",
        "azure": r"\bazure\b",
        "kubernetes": r"\b(kubernetes|k8s)\b",
        "postgresql": r"\b(postgresql|postgres)\b",
        "javascript": r"\bjavascript\b",
        "react": r"\breact\b",
    }

#Expresion manual
  @staticmethod
  def is_skill_in_text(skill, text):
    """Verifica dinámicamente si cualquier habilidad escrita por el usuario aparece en la descripción."""
    if not isinstance(text, str) or not skill:
      return False

    skill_clean = skill.strip().lower()
    text_clean = text.lower()

    # Patrón para caracteres especiales como C++, C#, .NET, etc.
    pattern = (
        r"(?i)(?:\b|(?<=\s))"
        + re.escape(skill_clean)
        + r"(?:\b|(?=\s)|(?=[.,;!?]|$))"
    )
    return bool(re.search(pattern, text_clean))

#Extraccion de habilidades
  def extract_skills_from_text(self, text):
    if not isinstance(text, str):
      return []

    text_lower = text.lower()
    found_skills = []

    for skill_name, pattern in self.skills_catalog.items():
      if re.search(pattern, text_lower):
        found_skills.append(skill_name)

    return found_skills

#Integrador de DataFrame
  def process_jobs_dataframe(self, df):
    df_processed = df.copy()
    df_processed["habilidades_requeridas"] = df_processed[
        "descripcion_raw"
    ].apply(self.extract_skills_from_text)
    return df_processed