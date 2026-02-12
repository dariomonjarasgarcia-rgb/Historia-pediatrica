import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import json
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Unidad Pediátrica", layout="wide", page_icon="🏥")

# Intentamos cargar tu estilo premium si existe el archivo
try:
    from interface_premium import cargar_estilo_hospital
    cargar_estilo_hospital()
except:
    st.markdown("""<style> .stApp { background-color: #f0f2f6; } </style>""", unsafe_allow_html=True)

# --- 2. BASE DE DATOS LOCAL (ADMINISTRACIÓN) ---
def cargar_db():
    if os.path.exists("usuarios_v3.json"):
        with open("usuarios_v3.json", "r") as f: return json.load(f)
    return {"admin@gmail.com": {"password": "admin123", "role": "Admin", "activo": True}}

def guardar_db(db):
    with open("usuarios_v3.json", "w") as f: json.dump(db, f)

# --- 3. MOTOR PDF ---
class CLINIC_PDF(FPDF):
    def header(self):
        self.set_fill_color(240, 245, 250)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)
        nombre = st.session_state.get("datos_medico", "DR. DARIO MONJARAS")
        self.cell(0, 10, nombre.upper(), 0, 1, 'C')
        self.ln(15)
    def section_header(self, title):
        self.ln(2); self.set_font('Arial', 'B', 12); self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255); self.cell(0, 8, f"  {title}", 0, 1, 'L', fill=True); self.ln(3)

# --- 4. INICIALIZACIÓN ---
if "db" not in st.session_state: st.session_state["db"] = cargar_db()
if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
if "datos_medico" not in st.session_state: st.session_state["datos_medico"] = "Dr. Dario Monjaras"

# --- 5. LOGIN ---
if "autenticado" not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            st.title("📂 Acceso al Sistema")
            modo = st.radio("Acción", ["Entrar", "Registrarse"], horizontal=True)
            u_email = st.text_input("Usuario (Correo)")
            u_pass = st.text_input("Contraseña", type="password")
            if modo == "Entrar":
                if st.button("Ingresar", use_container_width=True, type="primary"):
                    db = st.session_state["db"]
                    if u_email in db and db[u_email]["password"] == u_pass:
                        if db[u_email].get("activo", False):
                            st.session_state.update({"autenticado": True, "user_email": u_email, "role": db[u_email]["role"]})
                            st.rerun()
                        else: st.error("⏳ Cuenta pendiente de activación.")
                    else: st.error("❌ Datos incorrectos.")
            else:
                if st.button("Crear Cuenta"):
                    db = st.session_state["db"]
                    if u_email not in db:
                        db[u_email] = {"password": u_pass, "role": "User", "activo": False}
                        guardar_db(db); st.success("✅ Registrado. Pide activación al Admin.")
                    else: st.warning("Ese correo ya existe.")
    st.stop()

# --- 6. BARRA LATERAL (ADMIN + PACIENTES) ---
with st.sidebar:
    st.write(f"🩺 **Médico:** {st.session_state['user_email']}")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.clear(); st.rerun()
    st.divider()

    # EL PANEL MAESTRO QUE ME PEDISTE
    if st.session_state["role"] == "Admin":
        with st.expander("👑 PANEL DE ACTIVACIÓN", expanded=True):
            db = st.session_state["db"]
            for email, info in list(db.items()):
                if email != "admin@gmail.com":
                    c_mail, c_btn = st.columns([2,1])
                    c_mail.write(f"{'✅' if info['activo'] else '⏳'} {email}")
                    if c_btn.button("Activar", key=f"btn_{email}"):
                        db[email]["activo"] = not db[email]["activo"]
                        guardar_db(db); st.rerun()
        st.divider()

    if st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True):
        p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
        st.session_state["lista_pacientes"][p_id] = {"nombre": "", "peso": "", "talla": "", "motivo": ""}
        st.session_state["paciente_actual"] = p_id

# --- 7. CUERPO PRINCIPAL ---
if "paciente_actual" in st.session_state:
    pac = st.session_state["lista_pacientes"][st.session_state["paciente_actual"]]
    st.header(f"Expediente: {pac['nombre'] or 'Nuevo'}")
    pac['nombre'] = st.text_input("Nombre del Paciente", pac['nombre'])
    pac['peso'] = st.text_input("Peso (kg)", pac['peso'])
    pac['talla'] = st.text_input("Talla (cm)", pac['talla'])
    pac['motivo'] = st.text_area("Notas Médicas", pac['motivo'])
    st.info("Los cambios se guardan mientras la sesión esté abierta.")
