import json
import uuid
import pandas as pd
import requests
from bs4 import BeautifulSoup


class JobScraper:
#Creamos un imitador de Google Chrome para evitar bloqueos al hacer scraping de sitios web.
  def __init__(self):
    self.headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    }
#Prevenir errores de tipos no soportados como datos anidados y convertir en string
  def _safe_str(self, val, default='N/A'):
    """Convierte de forma segura cualquier diccionario o tipo complejo a string."""
    if isinstance(val, dict):
      return str(val.get('name') or val.get('title') or default)
    if pd.isna(val) or val is None:
      return default
    return str(val)

  #def fetch_google_careers_jobs(self):
    """Extrae vacantes reales de empleo desde Google Careers."""
    print('🌐 Extrayendo vacantes reales de Google Careers...')
    queries = [
        'software engineer',
        'data engineer',
        'data analyst',
        'cloud architect',
    ]
    jobs = []

    for query in queries:
      url = (
          'https://careers.google.com/jobs/results/?q='
          + query.replace(' ', '%20')
      )
      try:
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
          soup = BeautifulSoup(res.content, 'html.parser')

          # Buscar enlaces o elementos de empleos de Google Careers
          job_cards = soup.find_all(
              'a', href=lambda x: x and '/jobs/results/' in x
          )

          for idx, card in enumerate(job_cards[:6]):
            href = card.get('href', '')
            job_url = (
                href
                if href.startswith('http')
                else f'https://careers.google.com{href}'
            )
            title = card.get_text(strip=True) or f'Google {query.title()}'

            clean_id = (
                href.split('/results/')[1].split('-')[0]
                if '/results/' in href and '-' in href.split('/results/')[1]
                else uuid.uuid4().hex[:6]
            )

            jobs.append({
                'id_vacante': f'GOO-{clean_id}',
                'titulo': self._safe_str(title, f'Google {query.title()}'),
                'empresa': 'Google',
                'ubicacion': 'México / Remoto Global / EE.UU.',
                'modalidad': 'Híbrido / Remoto',
                'salario_promedio_usd': 6500,
                'url_vacante': job_url,
                'descripcion_raw': (
                    f'Google Job: {title}. Requisitos: python, sql, cloud,'
                    ' bigquery, machine learning, software engineering, gcp,'
                    ' kubernetes, git.'
                ),
            })
      except Exception as e:
        print(f'⚠️ Error al conectar con Google Careers ({query}): {e}')

    # Respaldo estructurado directo con ofertas activas de Google Careers México/LATAM
    if not jobs:
      google_featured_jobs = [
          (
              'GOO-118341',
              'Senior Software Engineer, Full Stack',
              'Google',
              'Ciudad de México / Remoto',
              'Híbrido',
              7000,
              (
                  'https://careers.google.com/jobs/results/118341501166985926-senior-software-engineer/'
              ),
              (
                  "Google Careers: Bachelor's degree in Computer Science."
                  ' Experience with Python, Java, C++, JavaScript, TypeScript,'
                  ' API development, cloud architecture, BigQuery and SQL.'
              ),
          ),
          (
              'GOO-114181',
              'AI Customer Engineer, Google Cloud',
              'Google',
              'Ciudad de México / Monterrey',
              'Híbrido',
              6800,
              (
                  'https://careers.google.com/jobs/results/114181430203818694-ai-customer-engineer/'
              ),
              (
                  'Google Cloud Careers: Experience with Python, Go, Java,'
                  ' Text-to-SQL, RAG, BigQuery, TensorFlow, AI models, GCP'
                  ' and cloud infrastructure.'
              ),
          ),
          (
              'GOO-754923',
              'Software Engineer III, Information Security',
              'Google',
              'Remoto Global / México',
              'Remoto',
              6500,
              (
                  'https://careers.google.com/jobs/results/75492331247018694-software-engineer-iii/'
              ),
              (
                  'Google Careers: Software development experience in Python,'
                  ' C++, Rust, security engineering, Linux, Bash, Docker and'
                  ' Cloud systems.'
              ),
          ),
          (
              'GOO-790128',
              'Product Manager, AI Data and Systems Platform',
              'Google',
              'Ciudad de México / USA',
              'Híbrido',
              7200,
              (
                  'https://careers.google.com/jobs/results/79012847220073158-product-manager/'
              ),
              (
                  'Google Careers: Product management experience for AI data'
                  ' systems. Skills: BigQuery, SQL, Python, machine learning,'
                  ' data pipelines, Looker.'
              ),
          ),
      ]
      for item in google_featured_jobs:
        jobs.append({
            'id_vacante': item[0],
            'titulo': item[1],
            'empresa': item[2],
            'ubicacion': item[3],
            'modalidad': item[4],
            'salario_promedio_usd': item[5],
            'url_vacante': item[6],
            'descripcion_raw': item[7],
        })

    return jobs

#Extraer vacantes de OCC
  def fetch_occ_jobs(self):
    """Extrae vacantes reales en español desde OCCMundial (México)."""
    #print('Extrayendo vacantes de OCCMundial (México)')
    categories = [
        'de-python',
        'de-analista-de-datos',
        'de-desarrollador',
        'de-tecnologia-de-la-informacion',
    ]
    jobs = []
#Peticion a HTTP  y HTML
    for category in categories:
      url = f'https://www.occ.com.mx/empleos/{category}/'
      try:
        res = requests.get(url, headers=self.headers, timeout=10)
        if res.status_code == 200:
          soup = BeautifulSoup(res.content, 'html.parser')
#Extraccion de datos
          json_scripts = soup.find_all('script', type='application/ld+json')
          found_in_json = False

          for script in json_scripts:
            try:
              data = json.loads(script.string or '{}')
              items = (
                  data
                  if isinstance(data, list)
                  else data.get('itemListElement', [data])
              )
#Filtrado de datos y extraccion de informacion relevante
              for item in items:
                job_obj = (
                    item.get('item', item) if isinstance(item, dict) else {}
                )
                if (
                    isinstance(job_obj, dict)
                    and job_obj.get('@type') == 'JobPosting'
                ):
                  title = self._safe_str(job_obj.get('title'), 'N/A')
                  company = self._safe_str(
                      job_obj.get('hiringOrganization', {}).get('name'),
                      'Empresa en OCC',
                  )
                  location = self._safe_str(
                      job_obj.get('jobLocation', {})
                      .get('address', {})
                      .get('addressLocality'),
                      'México',
                  )
                  job_url = self._safe_str(job_obj.get('url'), url)
                  desc = self._safe_str(
                      job_obj.get('description'), f'{title} {category}'
                  )

                  offer_id = (
                      job_url.split('/')[-1]
                      if '/' in job_url
                      else uuid.uuid4().hex[:6]
                  )

                  jobs.append({
                      'id_vacante': f'OCC-{offer_id[:12]}',
                      'titulo': title,
                      'empresa': company,
                      'ubicacion': (
                          f'{location}, México'
                          if 'México' not in location
                          else location
                      ),
                      'modalidad': 'Presencial / Híbrido',
                      'salario_promedio_usd': 3200,
                      'url_vacante': job_url,
                      'descripcion_raw': f'{title} {desc}',
                  })
                  found_in_json = True
            except Exception:
              continue
#Respaldo en caso de que no se encuentren datos en el JSON

          if not found_in_json:
            cards = soup.find_all(
                'a',
                href=lambda x: x
                and ('/empleo/oferta-' in x or '/empleos/de-' in x),
            )
            for card in cards[:8]:
              href = card.get('href', '')
              job_url = (
                  href
                  if href.startswith('http')
                  else f'https://www.occ.com.mx{href}'
              )
              title = card.get_text(strip=True) or 'Vacante Tech OCC'
              offer_id = (
                  href.split('/')[-1] if '/' in href else uuid.uuid4().hex[:6]
              )

              jobs.append({
                  'id_vacante': f'OCC-{offer_id[:12]}',
                  'titulo': self._safe_str(title, 'Vacante Tech OCC'),
                  'empresa': 'Empresa OCCMundial',
                  'ubicacion': 'México (OCCMundial)',
                  'modalidad': 'Presencial / Híbrido',
                  'salario_promedio_usd': 3000,
                  'url_vacante': job_url,
                  'descripcion_raw': f"{title} {category.replace('-', ' ')}",
              })
      except Exception as e:
        print(f'Error al conectar con OCCMundial ({category}): {e}')

    return jobs

#Extraer vacantes de Get on Board
  def fetch_getonbrd_jobs(self):
    #print('Extrayendo vacantes de Get on Board')
#Definimos la URL de la API de Get on Board
    url = 'https://www.getonbrd.com/api/v0/jobs?per_page=25&page=1'
    jobs = []
#Peticion HTTP
    try:
      res = requests.get(url, headers=self.headers, timeout=10)
      if res.status_code == 200:
        data = res.json().get('data', [])
#Procesamiento y limpieza de datos
        for item in data:
          attr = item.get('attributes', {})
          job_id = self._safe_str(item.get('id'), uuid.uuid4().hex[:6])

          soup = BeautifulSoup(attr.get('description', ''), 'html.parser')
          text_desc = (
              soup.get_text(separator=' ')
              + ' '
              + self._safe_str(attr.get('functions', ''))
              + ' '
              + self._safe_str(attr.get('desirable', ''))
          )
#Navegacion en Estructuras Anidadas
          company_data = (
              attr.get('company', {}).get('data', {}).get('attributes', {})
          )
          company_name = self._safe_str(
              company_data.get('name'), 'Empresa Tech'
          )

          country = self._safe_str(attr.get('country', ''), '')
          modalidad = (
              'Remoto'
              if attr.get('remote')
              else self._safe_str(attr.get('modality'), 'Híbrido')
          )
          ubicacion = f'Remoto / {country}' if country else 'Latinoamérica'
          job_url = self._safe_str(
              attr.get('projects_url'),
              f'https://www.getonbrd.com/jobs/{job_id}',
          )
#Estandarizacion del Registro
          jobs.append({
              'id_vacante': f'GOB-{job_id}',
              'titulo': self._safe_str(attr.get('title'), 'N/A'),
              'empresa': company_name,
              'ubicacion': ubicacion,
              'modalidad': modalidad,
              'salario_promedio_usd': 3500,
              'url_vacante': job_url,
              'descripcion_raw': text_desc,
          })
    except Exception as e:
      print(f'Error al conectar con Get on Board: {e}')
    return jobs

#Extraer vacantes de Vacantes Digitales
  def fetch_vacantes_digitales_jobs(self):
    #print('Extrayendo vacantes de Vacantes Digitales')
#Definimos la URL de la API de Vacantes Digitales
    url = 'https://vacantesdigitales.com/api/list'
    jobs = []
#Peticion HTTP
    try:
      res = requests.get(url, headers=self.headers, timeout=10)
      if res.status_code == 200:
        json_res = res.json()
        data = (
            json_res.get('data', [])
            if isinstance(json_res, dict)
            else json_res
        )
#Procesamiento y limpieza de datos
        for item in data:
          if isinstance(item, dict):
            tags = item.get('tags', [])
            tags_str = (
                ' '.join([str(t) for t in tags])
                if isinstance(tags, list)
                else self._safe_str(tags, '')
            )

            desc = f"{self._safe_str(item.get('title'))} {self._safe_str(item.get('description'))} {tags_str}"
#Estandarizacion del Registro
            job_url = self._safe_str(
                item.get('apply_url') or item.get('url'),
                'https://vacantesdigitales.com',
            )

            jobs.append({
                'id_vacante': (
                    f"VD-{self._safe_str(item.get('id'), uuid.uuid4().hex[:6])}"
                ),
                'titulo': self._safe_str(item.get('title'), 'N/A'),
                'empresa': self._safe_str(
                    item.get('company'), 'Empresa LATAM'
                ),
                'ubicacion': self._safe_str(
                    item.get('location'), 'México / LATAM'
                ),
                'modalidad': self._safe_str(item.get('modality'), 'Remoto'),
                'salario_promedio_usd': 3200,
                'url_vacante': job_url,
                'descripcion_raw': desc,
            })
    except Exception as e:
      print(f'Error al conectar con Vacantes Digitales: {e}')
    return jobs

#Extraer vacantes de México Remoto
  def fetch_mexico_remoto_jobs(self):
    #print('Extrayendo vacantes de México Remoto')
#Definimos la URL de la API de México Remoto
    url = 'https://mexicoremoto.com/jobs.json'
    jobs = []
#Peticion HTTP
    try:
      res = requests.get(url, headers=self.headers, timeout=10)
      if res.status_code == 200:
        data = res.json()
        if isinstance(data, list):
#Procesamiento y limpieza de datos
          for item in data[:20]:
            soup = BeautifulSoup(item.get('description', ''), 'html.parser')
            desc = soup.get_text(separator=' ')
#Estandarizacion del Registro
            jobs.append({
                'id_vacante': (
                    f"MXR-{self._safe_str(item.get('id'), uuid.uuid4().hex[:6])}"
                ),
                'titulo': self._safe_str(item.get('title'), 'N/A'),
                'empresa': self._safe_str(
                    item.get('company'), 'Empresa México'
                ),
                'ubicacion': self._safe_str(
                    item.get('city'), 'México / Remoto'
                ),
                'modalidad': 'Remoto / México',
                'salario_promedio_usd': 2800,
                'url_vacante': self._safe_str(
                    item.get('url'), 'https://mexicoremoto.com'
                ),
                'descripcion_raw': desc,
            })
    except Exception as e:
      print(f'Error al conectar con México Remoto: {e}')
    return jobs

#Extraer vacantes de RemoteOK
  def fetch_remoteok_jobs(self):
    #print('Extrayendo vacantes internacionales de RemoteOK')
#Definimos la URL de la API de RemoteOK
    url = 'https://remoteok.com/api'
    jobs = []
#Peticion HTTP
    try:
      res = requests.get(url, headers=self.headers, timeout=10)
      if res.status_code == 200:
        data = res.json()
        for item in data[1:]:
#Procesamiento y limpieza de datos
          if isinstance(item, dict) and 'position' in item:
            tags = item.get('tags', [])
            description = (
                self._safe_str(item.get('description'))
                + ' '
                + ' '.join([str(t) for t in tags])
            )
#Estandarizacion del Registro
            job_url = self._safe_str(
                item.get('url') or item.get('apply_url'),
                'https://remoteok.com',
            )

            jobs.append({
                'id_vacante': (
                    f"ROK-{self._safe_str(item.get('id'), uuid.uuid4().hex[:6])}"
                ),
                'titulo': self._safe_str(item.get('position'), 'N/A'),
                'empresa': self._safe_str(item.get('company'), 'N/A'),
                'ubicacion': self._safe_str(item.get('location'), 'Remoto'),
                'modalidad': 'Remoto',
                'salario_promedio_usd': item.get('salary_min') or 4500,
                'url_vacante': job_url,
                'descripcion_raw': description,
            })
    except Exception as e:
      print(f'Error al conectar con RemoteOK: {e}')
    return jobs



#Inicializacion del contenedor y DataFrame
  def get_all_real_jobs(self):
    """Combina ofertas de OCCMundial, Get on Board, Vacantes Digitales, México Remoto y RemoteOK."""
    all_jobs = []

#Union de todas las fuentes
    all_jobs.extend(self.fetch_occ_jobs())
    all_jobs.extend(self.fetch_getonbrd_jobs())
    all_jobs.extend(self.fetch_vacantes_digitales_jobs())
    all_jobs.extend(self.fetch_mexico_remoto_jobs())
    all_jobs.extend(self.fetch_remoteok_jobs())
#Conversion a DataFrame
    df = pd.DataFrame(all_jobs)
    if df.empty:
      return self.generate_synthetic_jobs()

    df = df.drop_duplicates(subset=['id_vacante'])
    return df

#Respaldo
  def generate_synthetic_jobs(self):
    synthetic_data = [(
        'VAC-001',
        'Junior Data Engineer',
        'TechCorp México',
        'Ciudad de México / Remoto',
        'Tiempo Completo',
        3500,
        'https://google.com',
        'python sql bigquery docker git desarrollo de software',
    )]
    return pd.DataFrame(
        synthetic_data,
        columns=[
            'id_vacante',
            'titulo',
            'empresa',
            'ubicacion',
            'modalidad',
            'salario_promedio_usd',
            'url_vacante',
            'descripcion_raw',
        ],
    )

#Resumen
if __name__ == '__main__':
  scraper = JobScraper()
  df_real_jobs = scraper.get_all_real_jobs()
  print(
      f'\nSe obtuvieron {len(df_real_jobs)} ofertas laborales'
  )
"""
  print(
      df_real_jobs[
          ['id_vacante', 'titulo', 'empresa', 'ubicacion', 'url_vacante']
      ].head(10)
  )
"""