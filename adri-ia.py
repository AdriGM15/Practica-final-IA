import streamlit as st
from groq import Groq
import os
import glob
import re
import random  

st.set_page_config(
    page_title="🏛️ Historia Universal",
    layout="wide",
    initial_sidebar_state="expanded"
)

GIFS_HISTORICOS = [
    "img/canalhistoria.gif",  
    "img/mapahistoria.gif"
]

def obtener_gif_aleatorio():
    """Devuelve un GIF histórico aleatorio."""
    return random.choice(GIFS_HISTORICOS)

def limpiar_nombre_archivo(nombre):
    nombre_seguro = nombre.strip().lower().replace(" ", "_")
    return re.sub(r'[^a-z0-9_]', '', nombre_seguro)

def listar_chats():
    archivos = glob.glob("chat_*.txt")
    chats = []
    for archivo in archivos:
        nombre_limpio = archivo.replace("chat_", "").replace(".txt", "").replace("_", " ").capitalize()
        chats.append(nombre_limpio)
    chats.sort()
    return chats

def guardar_en_historial(nombre_chat, pregunta, respuesta):
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    with open(nombre_archivo, mode="a", encoding="utf-8") as archivo:
        archivo.write(f"Pregunta Usuario:\n{pregunta}\n")
        archivo.write(f"Respuesta IA:\n{respuesta}\n")
        archivo.write("--------------------------------------------------------------------------------\n")

def leer_historial(nombre_chat):
    if not nombre_chat:
        return ""
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    try:
        with open(nombre_archivo, mode="r", encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return ""
    
def obtener_historial_para_ia(nombre_chat):
    """Convierte el historial en formato para la IA."""
    contenido = leer_historial(nombre_chat)
    mensajes_ia = []
    
    if not contenido:
        return mensajes_ia

    bloques = contenido.split("--------------------------------------------------------------------------------\n")
    
    for bloque in bloques:
        if "Pregunta Usuario:" in bloque and "Respuesta IA:" in bloque:
            partes = bloque.split("Respuesta IA:\n")
            pregunta = partes[0].replace("Pregunta Usuario:\n", "").strip()
            respuesta = partes[1].strip()
            
            mensajes_ia.append({"role": "user", "content": pregunta})
            mensajes_ia.append({"role": "assistant", "content": respuesta})
            
    return mensajes_ia

def eliminar_chat_fisico(nombre_chat):
    nombre_seguro = limpiar_nombre_archivo(nombre_chat)
    nombre_archivo = f"chat_{nombre_seguro}.txt"
    if os.path.exists(nombre_archivo):
        os.remove(nombre_archivo)

def obtener_system_prompt(nivel):
    if nivel == "Básico":
        return "Eres un asistente de historia básico. Explica los eventos históricos de forma sencilla, usando ejemplos claros y fechas principales. Responde de forma breve pero informativa."
    elif nivel == "Medio":
        return "Eres un asistente de historia con conocimientos intermedios. Responde de forma estructurada, mencionando fechas clave, personajes importantes y contexto social/económico. Incluye análisis moderado."
    elif nivel == "Experto":
        return "Eres un historiador experto. Responde con análisis profundos, citando fuentes históricas, fechas exactas, causas y consecuencias detalladas. Ofrece perspectivas críticas y conexiones entre eventos."
    else:
        st.error("Por favor selecciona un nivel de especialización histórica.")
        return "Eres un asistente experto en historia universal."

with st.sidebar:
    st.markdown("### 📜 Asistente Historia")
    
    with st.expander("📖 Ayuda"):
        st.markdown("""
        **Civilizaciones:** Egipto, Roma, Grecia  
        **Edades:** Media, Renacimiento, Moderna  
        **Personajes:** Reyes, emperadores, científicos  
        **Eventos:** Guerras, revoluciones  
        
        **Niveles:** Básico (simple), Medio (con fechas), Experto (profundo)
        """)
    
    st.divider()
    
    st.markdown("#### 🗂️ Chats")
    
    lista_de_chats = listar_chats()
    
    if not lista_de_chats:
        lista_de_chats = ["Principal"]
        with open("chat_principal.txt", "w", encoding="utf-8") as archivo:
            archivo.write("")

    with st.popover("➕ Nuevo Chat"):
        nuevo_nombre = st.text_input("Nombre:", placeholder="Ej. Imperio Romano", value="")
        if st.button("Crear"):
            if nuevo_nombre.strip():
                nombre_formateado = nuevo_nombre.strip().capitalize()
                nombre_seguro = limpiar_nombre_archivo(nombre_formateado)
                with open(f"chat_{nombre_seguro}.txt", "w", encoding="utf-8") as archivo:
                    archivo.write("")
                st.session_state.chat_actual = nombre_formateado
                st.rerun()
            else:
                st.warning("Nombre vacío")
    
    if "chat_actual" not in st.session_state:
        st.session_state.chat_actual = lista_de_chats[0]
    
    if st.session_state.chat_actual not in lista_de_chats:
        st.session_state.chat_actual = lista_de_chats[0]

    chat_seleccionado = st.selectbox(
        "Seleccionar:",
        lista_de_chats,
        index=lista_de_chats.index(st.session_state.chat_actual) if st.session_state.chat_actual in lista_de_chats else 0,
        key="selector_chat",
        label_visibility="collapsed"
    )
    st.session_state.chat_actual = chat_seleccionado
    
    st.divider()
    st.markdown("#### ⬇️ Exportar")
    historial_bruto = leer_historial(st.session_state.chat_actual)
    
    st.download_button(
        label="⬇️ Descargar",
        data=historial_bruto,
        file_name=f"historial_{limpiar_nombre_archivo(st.session_state.chat_actual)}.txt",
        mime="text/plain",
        disabled=not bool(historial_bruto.strip()),
        use_container_width=True
    )
    
    st.divider()
    st.markdown("#### ⚠️ Zona Peligro")
    with st.popover("🗑️ Eliminar"):
        st.warning(f"¿Borrar '{st.session_state.chat_actual}'?")
        if st.button("Sí, borrar"):
            eliminar_chat_fisico(st.session_state.chat_actual)
            st.toast("Eliminado", icon="🗑️")
            nuevos_chats = listar_chats()
            st.session_state.chat_actual = nuevos_chats[0] if nuevos_chats else "Principal"
            st.rerun()
    
    st.divider()
    st.markdown("#### 📄 Archivo bruto")
    st.text_area(
        "Contenido",
        historial_bruto if historial_bruto else "Vacío",
        height=70,
        label_visibility="collapsed"
    )

st.title("🏛️ Historia Universal")
st.caption("Explora el pasado con Inteligencia Artificial")

with st.expander("📜 Manual de Usuario - ¿Cómo usar este asistente?"):
    st.markdown("""
    ### 🎯 ¿Qué es este asistente?
    Es una herramienta que te permite explorar la historia universal mediante conversaciones con Inteligencia Artificial.
    
    ### 📚 ¿Qué puedes preguntar?
    - **Civilizaciones antiguas**: Egipto, Roma, Grecia, Mesopotamia
    - **Edades históricas**: Edad Media, Renacimiento, Edad Moderna
    - **Personajes históricos**: Reyes, emperadores, científicos, artistas
    - **Eventos clave**: Guerras, revoluciones, descubrimientos
    
    ### ⚙️ ¿Cómo funciona?
    1. **Crea un chat** nuevo para cada tema histórico
    2. **Selecciona el nivel** de especialización (Básico/Medio/Experto)
    3. **Ajusta la temperatura** para respuestas más precisas o creativas
    4. **Escribe tu pregunta** y la IA te responderá
    5. **Exporta o elimina** chats según necesites
    
    ### 💡 Ejemplos:
    - *"¿Cuáles fueron las causas de la caída del Imperio Romano?"*
    - *"Explícame la Revolución Francesa paso a paso"*
    - *"¿Quién fue Alejandro Magno?"*
    """)

st.info(f"💬 Conversando en: **{st.session_state.chat_actual}**")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### 💬 Interfaz de Chat")
    historial_pantalla = obtener_historial_para_ia(st.session_state.chat_actual)
    contenedor_chat = st.container(height=450, border=True)
    with contenedor_chat:
        if not historial_pantalla:
            st.caption("📖 No hay mensajes. Escribe tu consulta abajo.")
        else:
            for mensaje in historial_pantalla:
                with st.chat_message(mensaje["role"]):
                    st.write(mensaje["content"])
                    if mensaje["role"] == "assistant":
                        gif_url = obtener_gif_aleatorio()
                        st.image(gif_url, width=150)
    
    prompt = st.chat_input("✍️ Escribe tu pregunta sobre historia aquí...")

with col2:
    st.markdown("### ⚙️ Parámetros")
    
    temperatura = st.slider(
        "🌡️ Temperatura",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Baja = precisa | Alta = creativa"
    )

    nivel = st.selectbox(
        "📊 Nivel",
        ["Básico", "Medio", "Experto"],
        index=0
    )

if prompt and prompt.strip():
    try:
        historial_previo = obtener_historial_para_ia(st.session_state.chat_actual)
        system_prompt = obtener_system_prompt(nivel)
        
        mensajes_completos = [
            {"role": "system", "content": system_prompt}
        ] + historial_previo + [
            {"role": "user", "content": prompt}
        ]
        
        cliente = Groq(api_key=st.secrets["GROQ_API_KEY"])
        respuesta = cliente.chat.completions.create(
            model="groq/compound-mini",
            messages=mensajes_completos,
            temperature=temperatura
        )
        
        texto_respuesta = respuesta.choices[0].message.content
        
        guardar_en_historial(st.session_state.chat_actual, prompt, texto_respuesta)
        st.rerun()
        
    except Exception as error:
        st.error(f"❌ Fallo en el enlace con la IA: {error}")