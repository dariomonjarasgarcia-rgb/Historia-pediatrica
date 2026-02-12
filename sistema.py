import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io
import json
import os
from interface_premium import cargar_estilo_hospital

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Unidad Pediátrica", layout="wide", page_icon="🏥")
cargar_estilo_hospital()

# --- BLOQUE DE SEGURIDAD REFORZADO (OCULTA MANAGE APP DEFINITIVAMENTE) ---
hide_streamlit_style = """
            <style>
            /* Ocultar botón negro 'Manage app' */
            button[title="Manage app"], 
            .stAppDeployButton, 
            div[data-testid="stStatusWidget"],
            header[data-testid="stHeader"] {
                display: none !important;
                max-height: 0px;
            }
            
            /* Ocultar menú de hamburguesa y pie de página */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Ajuste de margen superior tras ocultar el header */
            .block-container {padding-top: 1rem !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- MOTOR PDF PROFESIONAL ---
class CLINIC_PDF(FPDF):
    def header(self):
        self.set_fill_color(240, 245, 250)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)
        nombre_medico = st.session_state.get("datos_medico", "Dr. Dario Monjaras")
        self.cell(0, 10, nombre_medico.upper(), 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.set_text_color(100, 100, 100)
        sub = st.session_state.get("sub_encabezado", "Cédula Profesional | Especialidad")
        self.cell(0, 5, sub, 0, 1, 'C')
        self.ln(15)

    def section_header(self, title):
        self.ln(2)
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {title}", 0, 1, 'L', fill=True)
        self.ln(3)

    def add_info(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50, 50, 50)
        self.write(7, f"{label}: ")
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        text_val = str(value) if value and str(value).strip() != "" else "No referido / Negado"
        self.multi_cell(0, 7, text_val)
        self.ln(1)

# --- SISTEMA DE USUARIOS Y AUTORIZACIÓN ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f: return json.load(f)
    return {"admin": "medico2026"}

def cargar_autorizados():
    if os.path.exists("autorizados.json"):
        with open("autorizados.json", "r") as f: return json.load(f)
    return ["admin"]

def guardar_autorizados(lista):
    with open("autorizados.json", "w") as f: json.dump(lista, f)

def guardar_usuario(u, p):
    db = cargar_usuarios()
    db[u] = p
    with open("usuarios.json", "w") as f: json.dump(db, f)

# --- INICIALIZACIÓN ---
if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
if "datos_medico" not in st.session_state: st.session_state["datos_medico"] = "Dr. Dario Monjaras"
if "sub_encabezado" not in st.session_state: st.session_state["sub_encabezado"] = "Pediatra Neonatólogo | Cédula: 1234567"

# --- LOGIN ---
if "autenticado" not in st.session_state:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.container(border=True):
            st.title("📂 Expediente Clínico")
            modo = st.radio("Acción", ["Iniciar Sesión", "Registrarse"], horizontal=True)
            u_input = st.text_input("Usuario")
            p_input = st.text_input("Contraseña", type="password")
            
            if modo == "Iniciar Sesión":
                if st.button("Ingresar", use_container_width=True, type="primary"):
                    db_actual = cargar_usuarios()
                    auth_list = cargar_autorizados()
                    if u_input in db_actual and db_actual[u_input] == p_input:
                        if u_input in auth_list:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario_actual"] = u_input
                            st.rerun()
                        else:
                            st.error("⚠️ Cuenta pendiente de autorización por el Administrador.")
                    else:
                        st.error("Credenciales incorrectas")
            else:
                if st.button("Crear Cuenta", use_container_width=True):
                    if u_input and p_input:
                        guardar_usuario(u_input, p_input)
                        st.success("Usuario registrado. Solicite autorización al administrador.")
    st.stop()
            # --- SIDEBAR MEJORADA ---
with st.sidebar:
    st.markdown(f"### 🩺 Sesión: {st.session_state.get('usuario_actual')}")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()

    if st.session_state.get("usuario_actual") == "admin":
        with st.expander("👑 ACTIVAR USUARIOS", expanded=True):
            db_admin = cargar_usuarios()
            auth_list = cargar_autorizados()
            for user in list(db_admin.keys()):
                if user != "admin":
                    col_u, col_b = st.columns([2,1])
                    activo = user in auth_list
                    col_u.write(f"{'✅' if activo else '⏳'} {user}")
                    if col_b.button("OK", key=f"btn_{user}"):
                        if activo: auth_list.remove(user)
                        else: auth_list.append(user)
                        guardar_autorizados(auth_list)
                        st.rerun()
        st.divider()
    
    st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True, on_click=lambda: st.session_state.update({"paciente_actual": f"PAC-{datetime.now().strftime('%H%M%S')}"}))
    
    st.markdown("### 📋 Lista de Expedientes")
    if not st.session_state["lista_pacientes"]:
        st.info("No hay pacientes registrados.")
    else:
        for p_id, datos in st.session_state["lista_pacientes"].items():
            nombre_label = datos['nombre'] if datos['nombre'] else "Paciente sin nombre"
            if st.button(f"👤 {nombre_label}", key=p_id, use_container_width=True):
                st.session_state["paciente_actual"] = p_id
                st.rerun()

    st.divider()
    with st.expander("⚙️ Configuración PDF"):
        st.session_state["datos_medico"] = st.text_input("Nombre en PDF:", st.session_state["datos_medico"])
        st.session_state["sub_encabezado"] = st.text_area("Cédula / Especialidad:", st.session_state["sub_encabezado"])

# --- PANEL PRINCIPAL --- (Aquí sigue el resto de tu código igual)
if "paciente_actual" in st.session_state:
    p_id = st.session_state["paciente_actual"]
    # ... (El resto de tu lógica de pacientes se mantiene intacta)
