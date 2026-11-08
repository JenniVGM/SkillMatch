import plotly.express as px
import streamlit as st
from database import JobDatabase
from processor import SkillExtractor
from scraper import JobScraper

#Configutación de la página de Streamlit
st.set_page_config(
    page_title="SkillMatch",
    page_icon=" ",
    layout="wide",
)
#Diseño

# 1. Agregar Logo en la Barra Lateral (Reemplaza la URL o ruta local por tu imagen)
LOGO_URL = r"C:\Users\jenni\OneDrive - Universidad Autonoma de Coahuila\1. MCDO\4. Programacion Avanzada\Proyecto\Logo Job.jpg"  # O ruta local: "assets/logo.png"
st.sidebar.image(LOGO_URL, width=300)
st.sidebar.markdown(
    "<h3 style='text-align: center; color: #1E293B;'>By JenniVGM</h3>",
    unsafe_allow_html=True,
)

custom_css = """
<style>
    :root {
        --primary-color: #2563EB !important;
    }

    /* Fondo general */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'Inter', sans-serif;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }

    /* Títulos Principales */
    h1, h2, h3, h4 {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        padding: 10px 20px !important;
        border: none !important;
    }

    /* Texto inactivo (Gris) */
    button[data-baseweb="tab"] p,
    [data-testid="stTab"] p {
        color: #64748B !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* Texto activo (Azul) */
    button[aria-selected="true"] p,
    [aria-selected="true"] p {
        color: #2563EB !important;
        font-weight: 800 !important;
    }

    /* LÍNEA INDICADORA SUBRAYADA (AZUL) */
    div[data-baseweb="tab-highlight"],
    div[data-testid="stTabHighlight"],
    [data-baseweb="tab-highlight"] {
        background-color: #2563EB !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: #2563EB !important;
    }

    /* Tarjetas Métricas */
    div[data-testid="stMetric"] {
        background-color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        padding: 16px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #94A3B8 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Tarjetas Desplegables de Vacantes (Expanders) */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04) !important;
    }

    div[data-testid="stExpander"] summary span p {
        color: #0369A1 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    div[data-testid="stExpander"] div[role="region"] p,
    div[data-testid="stExpander"] div[role="region"] span,
    div[data-testid="stExpander"] div[role="region"] div {
        color: #0369A1 !important;
    }

    /* Badges de Habilidades */
    .skill-badge {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        margin-right: 6px;
        margin-bottom: 6px;
        font-size: 0.88rem;
        border: 1px solid #BAE6FD;
    }

    /* Botones de Enlace */
    div.stLinkButton > a {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        border: none !important;
        text-decoration: none !important;
        display: inline-block !important;
    }

    div.stLinkButton > a:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

#Cargar componentes y datos de la base de datos
@st.cache_resource
def load_components():
  scraper = JobScraper()
  extractor = SkillExtractor()
  db = JobDatabase()
#Si la base de datos está vacía, se realiza un scraping inicial y se guardan las vacantes procesadas
  if db.get_all_vacancies().empty:
    raw_df = scraper.get_all_real_jobs()
    processed_df = extractor.process_jobs_dataframe(raw_df)
    db.save_vacancies(processed_df)

  return extractor, db


extractor, db = load_components()

st.title("SkillMatch")
st.markdown("""
El match perfecto entre tus habilidades y tu trabajo ideal
""")

st.sidebar.header("Perfil del Candidato")

# Entrada de texto libre para ingresar CUALQUIER habilidad
custom_skills_input = st.sidebar.text_input(
    "Escribe tus habilidades:",
    value="python, sql",
    help=(
        "Separadas por comas"
    ),
)

# Convertir la entrada de texto en una lista
user_skills = [
    s.strip().lower() for s in custom_skills_input.split(",") if s.strip()
]

# Botón opcional para elegir sugerencias rápidas
st.sidebar.markdown("---")
#Boton de actualizacion de datos en tiempo real
if st.sidebar.button("Recargar"):
  scraper = JobScraper()
  raw_df = scraper.get_all_real_jobs()
  processed_df = extractor.process_jobs_dataframe(raw_df)
  db.save_vacancies(processed_df)
  st.sidebar.success("¡Base de datos actualizada!")

if not user_skills:
  st.warning(
      "Ingresa al menos una habilidad en el campo de texto izquierdo para"
      " comenzar."
  )
else:
  #Visualizacion de tabs para demanda de mercado y ofertas recomendadas
  tab1, tab2 = st.tabs(
      ["Demanda de Mercado", "Match de Vacantes"]
  )

  with tab1:
    st.subheader("Demanda y Salarios Promedio según tus Habilidades")
    demand_df = db.analyze_user_skills_demand(user_skills)

    if not demand_df.empty and demand_df["total_vacantes_que_la_piden"].sum() > 0:
      m1, m2, m3 = st.columns(3)
      m1.metric(
          "Habilidad Más Solicitada", demand_df.iloc[0]["habilidad"].upper()
      )
      m2.metric(
          "Total Vacantes",
          f"{demand_df.iloc[0]['total_vacantes_que_la_piden']} ofertas",
      )
      m3.metric(
          "Salario Promedio Global",
          f"${demand_df['salario_promedio_ofertas'].mean():,.2f} USD",
      )

      st.divider()
#Graficas de barras para demanda de habilidades y salarios promedio
      c1, c2 = st.columns(2)
      with c1:
        fig_bar = px.bar(
            demand_df,
            x="habilidad",
            y="total_vacantes_que_la_piden",
            title="Número de Vacantes por Habilidad Ingresada",
            color="total_vacantes_que_la_piden",
            color_continuous_scale="Blues",
            labels={
                "habilidad": "Habilidad",
                "total_vacantes_que_la_piden": "Total Vacantes",
            },
        )
        st.plotly_chart(fig_bar, use_container_width=True)

      with c2:
        fig_salary = px.bar(
            demand_df,
            x="habilidad",
            y="salario_promedio_ofertas",
            title="Salario Promedio Asociado (USD)",
            color="salario_promedio_ofertas",
            color_continuous_scale="Greens",
            labels={
                "habilidad": "Habilidad",
                "salario_promedio_ofertas": "Salario (USD)",
            },
        )
        st.plotly_chart(fig_salary, use_container_width=True)

      st.subheader("Detalle Estadístico de tus Habilidades")
      st.dataframe(demand_df, use_container_width=True)
    else:
      st.info(
          "No se encontraron ofertas activas para las habilidades especificadas"
          " en este momento. Intenta con otros términos."
      )
#Match de Score y Listado de Vacantes
  with tab2:
    st.subheader("Vacantes Compatibles con tu Perfil")
    match_df = db.calculate_match_score(user_skills)

    if match_df.empty:
      st.info(
          "No se encontraron ofertas que requieran las habilidades"
          " ingresadas."
      )
    else:
      for idx, row in match_df.iterrows():
        score = row["porcentaje_match"]

        if score >= 75:
          badge = f"Match Alto ({score}%)"
        elif score >= 50:
          badge = f"Match Medio ({score}%)"
        else:
          badge = f"Match Parcial ({score}%)"

        with st.expander(f"{row['titulo']} en {row['empresa']} — {badge}"):
          k1, k2, k3, k4 = st.columns(4)
          k1.write(f"**Ubicación:** {row['ubicacion']}")
          k2.write(f"**Modalidad:** {row['modalidad']}")
          k3.write(f"**Salario:** ${row['salario_promedio_usd']:,.2f} USD")
          k4.write(
              f"**Coincidencias:** {row['habilidades_coincidentes']} de"
              f" {row['total_habilidades_evaluadas']} skills evaluadas"
          )

          st.write("**Habilidades que requiere el empleo:**")
          skills_tags = [f"`{s}`" for s in row["habilidades_requeridas"]]
          st.markdown(" ".join(skills_tags) if skills_tags else "*(Ver descripción en el enlace)*")

          st.progress(int(score) / 100)

          job_url = row.get("url_vacante", "https://google.com")
          st.link_button("Ver Oferta Completa en la Web", job_url)