import streamlit as st
import os
from datetime import datetime, date
from PIL import Image
from pillow_heif import register_heif_opener
import pytz
import json  # <--- NUEVO
from github import Github # <--- NUEVO

# Habilitar soporte para fotos HEIC (iPhone)
register_heif_opener()

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Recuerdos",
    page_icon="❤️",
    layout="centered"
)

# ==========================================
# 🧠 CEREBRO: CONEXIÓN CON GITHUB (MODO DEBUG)
# ==========================================
def gestionar_votos(mes, dia, nuevo_voto=None):
    try:
        # 1. Intentamos leer el secreto
        if "GITHUB_TOKEN" not in st.secrets:
            st.error("❌ ERROR: No encuentro el GITHUB_TOKEN en los secretos de Streamlit.")
            return 50
            
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        
        # 2. Intentamos conectar con el repo
        # AQUI ES DONDE SUELE FALLAR: Asegúrate de que este nombre es EXACTO
        nombre_repo = "MrCordobex/calendario-ana" # <--- CAMBIA ESTO POR TU NOMBRE REAL SI ES OTRO
        
        try:
            repo = g.get_user().get_repo(nombre_repo)
        except Exception:
            st.error(f"❌ ERROR: No encuentro el repositorio '{nombre_repo}'. Revisa el nombre o los permisos del Token.")
            return 50

        # 3. Intentamos leer el archivo
        try:
            contents = repo.get_contents("votos.json")
            datos = json.loads(contents.decoded_content.decode())
        except Exception as e:
            st.error(f"❌ ERROR LEYENDO JSON: {e}. ¿Creaste el archivo votos.json en GitHub con {{}} dentro?")
            return 50
        
        clave = f"{mes}_{dia}"
        
        # 4. Intentamos escribir
        if nuevo_voto is not None:
            datos[clave] = nuevo_voto
            try:
                repo.update_file(contents.path, f"Voto dia {clave}", json.dumps(datos), contents.sha)
                return nuevo_voto
            except Exception as e:
                st.error(f"❌ ERROR ESCRIBIENDO: {e}. ¿Tu Token tiene permiso 'repo' completo?")
                return 50
            
        else:
            return datos.get(clave, 50)

    except Exception as e:
        st.error(f"❌ ERROR GENERAL: {e}")
        return 50
# # --- ESTILOS CSS (CSS HACKING PARA MEJORAR LA ESTÉTICA) ---
# --- ESTILOS CSS (ESTILO LIMPIO + POLAROID + POST-IT) ---
st.markdown("""
    <style>
    /* Centrar títulos */
    .main-title {
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        color: #ff4b4b;
        font-size: 3em;
        font-weight: bold;
    }
    .sub-title {
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        color: #555;
        font-size: 1.5em;
        margin-bottom: 20px;
    }
    .song-title {
        text-align: center;
        font-family: 'Helvetica', sans-serif;
        color: #333;
        font-size: 1.3em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    /* EFECTO POLAROID */
    div[data-testid="stImage"] img {
        border: 12px solid #ffffff;
        border-bottom: 40px solid #ffffff;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
        transform: rotate(-1.5deg);
        border-radius: 2px;
        transition: transform 0.3s ease;
    }
    div[data-testid="stImage"] img:hover {
        transform: rotate(0deg) scale(1.01);
    }

    /* Estilo para el desplegable */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #ff4b4b;
    }

    /* --- NUEVO: EL POST-IT AMARILLO --- */
    .postit {
        position: fixed;
        bottom: 80px; /* Lo subimos para que no lo tape la barra del móvil */
        right: 20px; /* Lo movemos a la DERECHA para que no lo tape el menú lateral */
        width: 140px;
        background-color: #ffeb3b;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        transform: rotate(-2deg); /* Lo giramos al otro lado */
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #333;
        z-index: 999999; /* Z-index exagerado para asegurar que salga encima de todo */
        text-align: center;
        border-radius: 2px;
        border: 1px solid #e6db55; /* Un borde sutil queda mejor */
    }
    /* Ocultar post-it en móviles muy pequeños si molesta (opcional) */
    @media (max-width: 640px) {
        .postit {
            width: 100px;
            font-size: 11px;
            padding: 10px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
zona_horaria = pytz.timezone('Europe/Madrid') 
hoy = datetime.now(zona_horaria).date()
# Descomenta la línea de abajo para probar fechas futuras:
# hoy = date(2024, 2, 14)

# Mapa para traducir el número del mes a tu carpeta
mapa_carpetas = {
    1: "01_Enero", 2: "02_Febrero", 3: "03_Marzo", 4: "04_Abril",
    5: "05_Mayo", 6: "06_Junio", 7: "07_Julio", 8: "08_Agosto",
    9: "09_Septiembre", 10: "10_Octubre", 11: "11_Noviembre", 12: "12_Diciembre"
}

# --- CONFIGURACIÓN DE MÚSICA ---
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

# --- LÓGICA INTELIGENTE DE URL (PARA LOS QRs) ---
params = st.query_params
fecha_defecto = hoy

if "mes" in params:
    try:
        mes_url = int(params["mes"])
        if 1 <= mes_url <= 12:
            fecha_defecto = date(hoy.year, mes_url, 1)
            if mes_url == hoy.month:
                fecha_defecto = hoy
    except:
        pass

# --- BARRA LATERAL (CALENDARIO + INSTRUCCIONES) ---
with st.sidebar:
    
    # --- NUEVO: BOTÓN DESPLEGABLE CON INSTRUCCIONES ---
    with st.expander("🎁 ¿Cómo funciona el regalo?"):
        st.markdown("""
        **¡Holii!** Bienvenido a tu calendario infinito. ❤️
        
        1. **📸 Foto Diaria:** Cada día se desbloquea una foto nueva automáticamente. La foto se ha tomado en el mes en el que se desbloquea :)
        2. **🚫 Sin Trampas:** Si intentas seleccionar un día futuro, el sistema no te dejará verlo jeje
        3. **🎶 Música:** Cada mes tiene su propia banda sonora. Dale al play debajo de la foto
        4. **🔙 Recuerdos:** Puedes usar el calendario de abajo para volver a ver días pasados
        """)
    
    st.write("---") # Separador visual

    st.header("📅 Navegación")
    st.write("Selecciona un día especial:")
    
    fecha_seleccionada = st.date_input(
        "Calendario",
        value=fecha_defecto,
        min_value=date(hoy.year, 1, 1),
        max_value=date(hoy.year, 12, 31)
    )
    
    st.write("---")
    st.caption("❤️ Hecho con cariño")

# --- PÁGINA PRINCIPAL ---

mes_nombre = fecha_seleccionada.strftime("%B")
nombres_meses_es = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
mes_esp = nombres_meses_es[fecha_seleccionada.month]

# --- NUEVO: BARRA DE PROGRESO ---
# 1. Calculamos el día del año (ej: día 4 de 366)
dia_anio = fecha_seleccionada.timetuple().tm_yday
dias_totales_anio = 366 if fecha_seleccionada.year % 4 == 0 else 365
porcentaje = dia_anio / dias_totales_anio

# 2. Texto de la barra (Menos ñoño, más limpio)
st.caption(f"Capítulo {dia_anio} de {dias_totales_anio}")
st.progress(porcentaje)

# --- NUEVO: POST-IT (DÍAS JUNTOS) ---
fecha_inicio = date(2019, 12, 7) # Vuestra fecha
dias_juntos = (hoy - fecha_inicio).days # Cálculo de días

st.markdown(f"""
    <div class='postit'>
        <b>Días Juntitos:</b><br>
        <span style='font-size: 20px'>{dias_juntos}</span>
        <br>❤️
    </div>
""", unsafe_allow_html=True)

# -------------------------------

st.markdown(f"<div class='main-title'>Nuestros recuerdos</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>Fotito del <b>{fecha_seleccionada.day} de {mes_esp}</b></div>", unsafe_allow_html=True)

# 2. Lógica de BLOQUEO
if fecha_seleccionada > hoy:
    st.divider()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.error("¡Alto ahí, viajera del tiempo! ⏳")
        st.write(f"Hoy es {hoy.day} de {nombres_meses_es[hoy.month]}. No puedes ver el futuro TRAMPOSA")
        st.image("https://media.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif")

else:
    carpeta = mapa_carpetas.get(fecha_seleccionada.month)
    dia = fecha_seleccionada.day
    
    ruta_carpeta = os.path.join("Fotos", carpeta)
    foto_encontrada = None
    
    if os.path.exists(ruta_carpeta):
        archivos = os.listdir(ruta_carpeta)
        for archivo in archivos:
            # Convertimos el nombre a minúsculas para comparar
            if archivo.lower().startswith(f"{dia}."):
                foto_encontrada = os.path.join(ruta_carpeta, archivo)
                break
    st.divider()
    
    if foto_encontrada:
        image = Image.open(foto_encontrada)
        st.image(image, use_column_width=True)

        # =========================================================
        # NUEVO: CRINGE-O-METRO (CON MEMORIA EN LA NUBE)
        # =========================================================
        st.write("") # Un poco de aire
        st.markdown("**🧐 ¿Qué nota le damos al outfit/careto?**")
        
        # 1. Recuperamos el voto guardado en GitHub (si existe)
        valor_guardado = gestionar_votos(fecha_seleccionada.month, fecha_seleccionada.day)

        # 2. Mostramos el slider empezando en el valor guardado
        rating = st.slider(
            "Puntúa:", 
            0, 100, 
            value=valor_guardado, 
            key=f"slider_{dia}_{fecha_seleccionada.month}", # Clave única para no mezclar días
            label_visibility="collapsed"
        )
        
        # 3. Si el usuario mueve el slider, guardamos el nuevo valor
        if rating != valor_guardado:
            gestionar_votos(fecha_seleccionada.month, fecha_seleccionada.day, rating)
            st.toast("¡Nota guardada para siempre! ☁️", icon="✅")

        if rating < 20:
            st.warning("🤢 Madre de dios...  Pedro borra esto, por favor")
        elif rating < 50:
            st.info("😅 Bueno, se intentó. No es nuestro mejor día")
        elif rating < 80:
            st.success("😎 Ni tan mal ehhhhh. Tenemos rollito")
        else:
            st.success("🔥 ¡DIOSES DEL OLIMPO! Vaya fotón")
        
        # =========================================================
        
        # --- AQUI VA LA MÚSICA ---
        link_cancion = musica_por_mes.get(fecha_seleccionada.month)
        if link_cancion and len(link_cancion) > 5:
            # 1. Añadimos espacio (salto de línea)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. Título más grande y con estilo propio
            st.markdown(f"<div class='song-title'>🎶 Nuestra canción de {mes_esp}</div>", unsafe_allow_html=True)
            
            # 3. Vídeo más pequeño usando columnas
            col_izq, col_centro, col_der = st.columns([1, 2, 1])
            with col_centro:
                st.video(link_cancion)

        if fecha_seleccionada == hoy:
            st.balloons()
            
        txt_path = foto_encontrada.rsplit('.', 1)[0] + ".txt"
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                st.info(f.read())
                
    else:
        st.warning(f"Ups, parece que para el día {dia} de {mes_esp} se me olvidó subir la foto... ¡Pídeme un beso de compensación! 😘")