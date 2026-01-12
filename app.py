import streamlit as st
import os
from datetime import datetime, date
from PIL import Image
from pillow_heif import register_heif_opener
import pytz
import json
from github import Github
import pandas as pd # <--- NUEVO: Para las gráficas

# Habilitar soporte para fotos HEIC (iPhone)
register_heif_opener()

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Recuerdos",
    page_icon="❤️",
    layout="centered"
)

# ==========================================
# 🧠 CEREBRO: CONEXIÓN CON GITHUB
# ==========================================
def obtener_conexion_repo():
    """Función auxiliar para conectar al repo sin repetir código"""
    try:
        if "GITHUB_TOKEN" not in st.secrets:
            st.error("❌ Falta el Token en Secrets.")
            return None
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        # ⚠️⚠️ PON AQUÍ TU NOMBRE DE REPO REAL ⚠️⚠️
        nombre_repo = "MrCordobex/streamlit-test-deploy" 
        return g.get_repo(nombre_repo)
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return None

def gestionar_votos(mes, dia, nuevo_voto=None):
    repo = obtener_conexion_repo()
    if not repo: return 50
    
    try:
        contents = repo.get_contents("votos.json")
        datos = json.loads(contents.decoded_content.decode())
        
        clave = f"{mes}_{dia}"
        
        if nuevo_voto is not None:
            datos[clave] = nuevo_voto
            repo.update_file(contents.path, f"Voto dia {clave}", json.dumps(datos), contents.sha)
            return nuevo_voto
        else:
            return datos.get(clave, 50) # 50 por defecto
    except Exception as e:
        print(f"Error gestión votos: {e}")
        return 50

def obtener_todos_los_datos():
    """Descarga todos los votos para las estadísticas"""
    repo = obtener_conexion_repo()
    if not repo: return {}
    try:
        contents = repo.get_contents("votos.json")
        return json.loads(contents.decoded_content.decode())
    except:
        return {}

# ==========================================
# 🎨 ESTILOS CSS
# ==========================================
st.markdown("""
    <style>
    .main-title { text-align: center; font-family: 'Helvetica', sans-serif; color: #ff4b4b; font-size: 3em; font-weight: bold; }
    .sub-title { text-align: center; color: #555; font-size: 1.5em; margin-bottom: 20px; }
    .song-title { text-align: center; color: #333; font-size: 1.3em; font-weight: bold; margin-top: 20px; }
    div[data-testid="stImage"] img {
        border: 12px solid #ffffff; border-bottom: 40px solid #ffffff;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2); transform: rotate(-1.5deg);
        border-radius: 2px; transition: transform 0.3s ease;
    }
    div[data-testid="stImage"] img:hover { transform: rotate(0deg) scale(1.01); }
    .postit {
        position: fixed; bottom: 80px; right: 20px; width: 140px;
        background-color: #ffeb3b; padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3); transform: rotate(-2deg);
        font-family: 'Courier New', monospace; font-size: 14px; color: #333;
        z-index: 999999; text-align: center; border-radius: 2px; border: 1px solid #e6db55;
    }
    @media (max-width: 640px) { .postit { width: 100px; font-size: 11px; padding: 10px; } }
    </style>
""", unsafe_allow_html=True)

# --- DATOS GLOBALES ---
zona_horaria = pytz.timezone('Europe/Madrid') 
hoy = datetime.now(zona_horaria).date()
# hoy = date(2024, 12, 31) # Descomentar para pruebas

mapa_carpetas = {
    1: "01_Enero", 2: "02_Febrero", 3: "03_Marzo", 4: "04_Abril",
    5: "05_Mayo", 6: "06_Junio", 7: "07_Julio", 8: "08_Agosto",
    9: "09_Septiembre", 10: "10_Octubre", 11: "11_Noviembre", 12: "12_Diciembre"
}
musica_por_mes = {
    1: "https://www.youtube.com/watch?v=kw5p7Azmh2Y&list=RDkw5p7Azmh2Y&start_radio=1",
    2: "https://www.youtube.com/watch?v=0qdDDFkheVw&list=RD0qdDDFkheVw&start_radio=1",
    3: "https://www.youtube.com/watch?v=5SXrZh03-pI&list=RD5SXrZh03-pI&start_radio=1",
    4: "https://www.youtube.com/watch?v=KgJzb_c2iiM&list=RDKgJzb_c2iiM&start_radio=1",
    5: "https://www.youtube.com/watch?v=fgLEhuSd64I&list=RDfgLEhuSd64I&start_radio=1",
    6: "https://www.youtube.com/watch?v=VEfkNHTjgs8&list=RDVEfkNHTjgs8&start_radio=1",
    7: "https://www.youtube.com/watch?v=PSjeJrDI4a4&list=RDPSjeJrDI4a4&start_radio=1",
    8: "https://www.youtube.com/watch?v=f41rIgQF-Mw&list=RDf41rIgQF-Mw&start_radio=1",
    9: "https://www.youtube.com/watch?v=BH8uWpXCLIM&list=RDBH8uWpXCLIM&start_radio=1",
    10: "https://www.youtube.com/watch?v=XM5DdGkRP40&list=RDXM5DdGkRP40&start_radio=1",
    11: "https://www.youtube.com/watch?v=TTzrFxeBiUQ&list=RDTTzrFxeBiUQ&start_radio=1",
    12: "https://www.youtube.com/watch?v=BaTM-84Akk8&list=RDBaTM-84Akk8&start_radio=1"
}
nombres_meses_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ==========================================
# 📊 PÁGINA DE ESTADÍSTICAS (CORREGIDO ORDEN)
# ==========================================
def ver_estadisticas():
    st.markdown(f"<div class='main-title'>📊 Estadísticas</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>Pedro no se ha podido resistir...</div>", unsafe_allow_html=True)
    st.write("")

    # 1. Recuperar datos
    raw_data = obtener_todos_los_datos()
    
    # 2. Selector de Filtro
    filtro = st.selectbox("¿Qué quieres analizar?", ["Todo el Año"] + names_meses_slice)
    
    # 3. Definir Rango de Fechas
    anio_actual = hoy.year
    
    if filtro == "Todo el Año":
        start_date = date(anio_actual, 1, 1)
        end_date = hoy 
        titulo_grafica = "Evolución de notas del Año"
    else:
        mes_idx = nombres_meses_es.index(filtro)
        
        if mes_idx > hoy.month:
            st.warning(f"¡Aún no hemos llegado a {filtro}! Paciencia viajera del tiempo.")
            return
            
        start_date = date(anio_actual, mes_idx, 1)
        
        if mes_idx == hoy.month:
            end_date = hoy
        else:
            if mes_idx == 12:
                end_date = date(anio_actual, 12, 31)
            else:
                end_date = date(anio_actual, mes_idx + 1, 1) - pd.Timedelta(days=1)
                
        titulo_grafica = f"Evolución de notas en {filtro}"

    # 4. Generar DataFrame
    rango_fechas = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame(rango_fechas, columns=['Fecha'])
    
    def buscar_nota(fecha):
        clave = f"{fecha.month}_{fecha.day}"
        return raw_data.get(clave, None)

    df['Nota'] = df['Fecha'].apply(buscar_nota)
    df['Nota'] = df['Nota'].fillna(50)
    
    # Creamos la columna Día solo para los textos de abajo (mejor/peor foto), 
    # pero NO la usaremos para la gráfica.
    def formatear_fecha(fecha):
        mes_nombre = nombres_meses_es[fecha.month]
        return f"{fecha.day} de {mes_nombre}"
        
    df['Día'] = df['Fecha'].apply(formatear_fecha)
    
    # 6. Calcular Media y Pintar
    media = df['Nota'].mean()
    df['Media'] = media
    
    st.caption(f"📈 {titulo_grafica} (Media: {media:.1f})")
    
    # --- CAMBIO IMPORTANTE AQUÍ ---
    # Usamos x='Fecha' en vez de 'Día' para que se ordene cronológicamente
    st.line_chart(df, x='Fecha', y=['Nota', 'Media'], color=["#ff4b4b", "#888888"])

    st.divider()

    # --- ZONA DE HONOR Y HORROR ---
    col_best, col_worst = st.columns(2)
    
    # --- 🏆 LA MEJOR FOTO ---
    with col_best:
        st.markdown("<h3 style='text-align: center; color: #4CAF50;'>🏆 La Mejor</h3>", unsafe_allow_html=True)
        idx_max = df['Nota'].idxmax()
        mejor_row = df.loc[idx_max]
        
        f_mejor = mejor_row['Fecha']
        carpeta = mapa_carpetas.get(f_mejor.month)
        ruta = os.path.join("Fotos", carpeta)
        archivo_best = None
        
        if os.path.exists(ruta):
            for f in os.listdir(ruta):
                if f.lower().startswith(f"{f_mejor.day}."):
                    archivo_best = os.path.join(ruta, f)
                    break
        
        if archivo_best:
            st.image(Image.open(archivo_best), caption=f"Nota: {mejor_row['Nota']}", use_column_width=True)
            # Aquí sí usamos la columna 'Día' porque es texto para leer
            st.success(f"{mejor_row['Día']}")
        else:
            st.info("Sin foto ganadora aún")
    
    # --- 🧟 LA PEOR FOTO ---
    with col_worst:
        st.markdown("<h3 style='text-align: center; color: #ff4b4b;'>🧟 La Peor</h3>", unsafe_allow_html=True)
        idx_min = df['Nota'].idxmin()
        peor_row = df.loc[idx_min]
        
        f_peor = peor_row['Fecha']
        carpeta = mapa_carpetas.get(f_peor.month)
        ruta = os.path.join("Fotos", carpeta)
        archivo_worst = None
        
        if os.path.exists(ruta):
            for f in os.listdir(ruta):
                if f.lower().startswith(f"{f_peor.day}."):
                    archivo_worst = os.path.join(ruta, f)
                    break
        
        if archivo_worst:
            st.image(Image.open(archivo_worst), caption=f"Nota: {peor_row['Nota']}", use_column_width=True)
            st.error(f"{peor_row['Día']}")
        else:
            st.info("Sin foto perdedora aún")
# ==========================================
# 📅 PÁGINA DEL CALENDARIO (TU CÓDIGO ACTUAL)
# ==========================================
def ver_calendario():
    # LÓGICA URL
    params = st.query_params
    fecha_defecto = hoy
    if "mes" in params:
        try:
            mes_url = int(params["mes"])
            if 1 <= mes_url <= 12:
                fecha_defecto = date(hoy.year, mes_url, 1)
                if mes_url == hoy.month: fecha_defecto = hoy
        except: pass

    # BARRA LATERAL DEL CALENDARIO
    with st.sidebar:
        with st.expander("🎁 ¿Cómo funciona el regalo?"):
            st.markdown("""
            **¡Holii!** Bienvenido a tu calendario infinito. ❤️
            1. **📸 Foto Diaria:** Cada día se desbloquea una foto nueva.
            2. **🚫 Sin Trampas:** No puedes ver el futuro.
            3. **🎶 Música:** Dale al play.
            4. **🔙 Recuerdos:** Usa el calendario.
            """)
        st.write("---")
        st.header("📅 Navegación")
        fecha_seleccionada = st.date_input("Calendario", value=fecha_defecto, min_value=date(hoy.year, 1, 1), max_value=date(hoy.year, 12, 31))
        st.write("---")

    # CUERPO PRINCIPAL
    mes_esp = nombres_meses_es[fecha_seleccionada.month]
    dia_anio = fecha_seleccionada.timetuple().tm_yday
    dias_totales_anio = 366 if fecha_seleccionada.year % 4 == 0 else 365
    porcentaje = dia_anio / dias_totales_anio
    st.caption(f"Capítulo {dia_anio} de {dias_totales_anio}")
    st.progress(porcentaje)
    
    # POST-IT
    fecha_inicio = date(2019, 12, 7)
    dias_juntos = (hoy - fecha_inicio).days
    st.markdown(f"<div class='postit'><b>Días Juntitos:</b><br><span style='font-size: 20px'>{dias_juntos}</span><br>❤️</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='main-title'>Nuestros recuerdos</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>Fotito del <b>{fecha_seleccionada.day} de {mes_esp}</b></div>", unsafe_allow_html=True)

    if fecha_seleccionada > hoy:
        st.divider()
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.error("¡Alto ahí! ⏳")
            st.write(f"Hoy es {hoy.day}. No puedes ver el futuro TRAMPOSA")
            st.image("https://media.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif")
    else:
        carpeta = mapa_carpetas.get(fecha_seleccionada.month)
        dia = fecha_seleccionada.day
        ruta_carpeta = os.path.join("Fotos", carpeta)
        foto_encontrada = None
        if os.path.exists(ruta_carpeta):
            for archivo in os.listdir(ruta_carpeta):
                if archivo.lower().startswith(f"{dia}."):
                    foto_encontrada = os.path.join(ruta_carpeta, archivo)
                    break
        st.divider()
        if foto_encontrada:
            image = Image.open(foto_encontrada)
            st.image(image, use_column_width=True)
            
            # CRINGE-O-METRO
            st.write("")
            st.markdown("**🧐 ¿Qué nota le damos al outfit/careto?**")
            valor_guardado = gestionar_votos(fecha_seleccionada.month, fecha_seleccionada.day)
            rating = st.slider("Puntúa:", 0, 100, value=valor_guardado, key=f"sl_{dia}_{fecha_seleccionada.month}", label_visibility="collapsed")
            
            if rating != valor_guardado:
                gestionar_votos(fecha_seleccionada.month, fecha_seleccionada.day, rating)
                st.toast("Nota guardada! ☁️", icon="✅")

            if rating < 20: st.warning("🤢 Madre de dios... Pedro borra esto.")
            elif rating < 50: st.info("😅 Bueno, se intentó.")
            elif rating < 80: st.success("😎 Ni tan mal ehhhhh.")
            else: st.success("🔥 ¡DIOSES DEL OLIMPO! Vaya fotón")
            
            # MÚSICA
            link_cancion = musica_por_mes.get(fecha_seleccionada.month)
            if link_cancion and len(link_cancion) > 5:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<div class='song-title'>🎶 Nuestra canción de {mes_esp}</div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1,2,1])
                with c2: st.video(link_cancion)
            
            if fecha_seleccionada == hoy: st.balloons()
            txt_path = foto_encontrada.rsplit('.', 1)[0] + ".txt"
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as f: st.info(f.read())
        else:
            st.warning(f"Ups, falta la foto del día {dia}... 😘")


# ==========================================
# 🚦 CONTROLADOR DE NAVEGACIÓN (MAIN)
# ==========================================
# Variable para controlar la lista de meses en el filtro
names_meses_slice = nombres_meses_es[1:]

# Inicializar estado de página
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "Calendario"

# BARRA LATERAL COMÚN (BOTONES)
with st.sidebar:
    st.title("Menú")
    if st.button("📅 Ver Calendario", use_container_width=True):
        st.session_state.pagina_actual = "Calendario"
    
    if st.button("📊 Ver Estadísticas", use_container_width=True):
        st.session_state.pagina_actual = "Stats"
    
    st.write("---")

# MOSTRAR LA PÁGINA QUE TOQUE
if st.session_state.pagina_actual == "Calendario":
    ver_calendario()
else:
    ver_estadisticas()