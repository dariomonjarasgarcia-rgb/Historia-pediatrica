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

# --- SISTEMA DE LOGIN Y PERSISTENCIA ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f: return json.load(f)
    return {"admin": "medico2026"}

if "db_usuarios" not in st.session_state: st.session_state["db_usuarios"] = cargar_usuarios()
if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
if "datos_medico" not in st.session_state: st.session_state["datos_medico"] = "Dr. Dario Monjaras"
if "sub_encabezado" not in st.session_state: st.session_state["sub_encabezado"] = "Pediatra Neonatólogo | Cédula: 1234567"

# --- LÓGICA DE ACCESO ---
if "autenticado" not in st.session_state:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.container(border=True):
            st.title("🏥 Acceso al Sistema")
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Ingresar", use_container_width=True, type="primary"):
                if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- SIDEBAR (BARRA LATERAL) ---
with st.sidebar:
    st.markdown(f"### 🩺 Bienvenido, {st.session_state.get('datos_medico')}")
    if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
        del st.session_state["autenticado"]
        st.rerun()
    st.divider()
    st.markdown("### ⚙️ Configuración del PDF")
    st.session_state["datos_medico"] = st.text_input("Nombre del Médico:", st.session_state["datos_medico"])
    st.session_state["sub_encabezado"] = st.text_area("Datos de contacto/Cédula:", st.session_state["sub_encabezado"])
    st.divider()
    
    if st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True):
        p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
        st.session_state["lista_pacientes"][p_id] = {
            "nombre": "", "f_nac": date(2020,1,1), "edad": "", "sexo": "M",
            "fc": "", "fr": "", "sat": "", "temp": "", "peso": "", "talla": "",
            "ahf": "", "prenatales": "", "natales": "", "vacunas": "", "alimentacion": "", "desarrollo": "",
            "motivo": "", "as_digestivo": "", "as_cardio": "", "as_urinario": "", "as_resp": "",
            "as_neuro": "", "as_piel": "", "as_musculo": "",
            "exploracion": "", "dx": "", "plan": "", "receta_texto": ""
        }
        st.session_state["paciente_actual"] = p_id
        st.rerun()
    
    opciones = list(st.session_state["lista_pacientes"].keys())
    if opciones:
        st.session_state["paciente_actual"] = st.selectbox("📂 Seleccionar Expediente:", opciones)

# --- PANEL PRINCIPAL ---
if "paciente_actual" in st.session_state:
    pac = st.session_state["lista_pacientes"][st.session_state["paciente_actual"]]
    st.markdown(f"<h1 style='text-align: center; color: #003366;'>🧑‍⚕️ {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}</h1>", unsafe_allow_html=True)
    
    t = st.tabs(["📋 Filiación", "🧬 Antecedentes", "🫁 Sistemas", "🔍 Exploración", "📝 DX/Plan", "💊 Receta", "📈 Evolución"])

    with t[0]: # FILIACIÓN
        with st.container(border=True):
            st.subheader("Datos de Identificación")
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'] = c1.date_input("Fecha de Nacimiento:", pac['f_nac'])
            pac['edad'] = c2.text_input("Edad Actual:", value=pac['edad'])
            pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
        with st.container(border=True):
            st.subheader("📊 Signos Vitales y Antropometría")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'] = s1.text_input("F.C. (lpm):", pac['fc']), s2.text_input("F.R. (rpm):", pac['fr'])
            pac['sat'], pac['temp'] = s3.text_input("SatO2 (%):", pac['sat']), s4.text_input("Temp (°C):", pac['temp'])
            s5, s6 = st.columns(2)
            pac['peso'], pac['talla'] = s5.text_input("Peso (kg):", pac['peso']), s6.text_input("Talla (cm):", pac['talla'])

    with t[1]: # ANTECEDENTES
        with st.container(border=True):
            col1, col2 = st.columns(2)
            pac['ahf'] = col1.text_area("Heredofamiliares:", value=pac['ahf'])
            pac['prenatales'] = col2.text_area("Prenatales:", value=pac['prenatales'])
            pac['natales'] = col1.text_area("Natales:", value=pac['natales'])
            pac['vacunas'] = col2.text_area("Vacunas:", value=pac['vacunas'])
            pac['alimentacion'] = col1.text_area("Alimentación:", value=pac['alimentacion'])
            pac['desarrollo'] = col2.text_area("Hitos Desarrollo:", value=pac['desarrollo'])

    with t[2]: # SISTEMAS
        with st.container(border=True):
            pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'], height=120)
            st.divider()
            ca, cb = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = ca.text_area("A. Digestivo:", value=pac['as_digestivo']), cb.text_area("A. Respiratorio:", value=pac['as_resp'])
            pac['as_cardio'], pac['as_urinario'] = ca.text_area("A. Cardiovascular:", value=pac['as_cardio']), cb.text_area("A. Genitourinario:", value=pac['as_urinario'])
            pac['as_neuro'], pac['as_piel'] = ca.text_area("A. Neurológico:", value=pac['as_neuro']), cb.text_area("Piel y Faneras:", value=pac['as_piel'])

    with t[3]: # EXPLORACIÓN
        pac['exploracion'] = st.text_area("Hallazgos de Exploración Física:", value=pac['exploracion'], height=350)

    with t[4]: # DX / PLAN / GENERAR PDF
        with st.container(border=True):
            pac['dx'] = st.text_area("Impresión Diagnóstica:", value=pac['dx'])
            pac['plan'] = st.text_area("Plan Terapéutico:", value=pac['plan'])
        
        if st.button("🖨️ GENERAR EXPEDIENTE COMPLETO", type="primary", use_container_width=True):
            pdf = CLINIC_PDF()
            pdf.add_page()
            pdf.section_header("1. DATOS DE FILIACIÓN Y SOMATOMETRÍA")
            pdf.add_info("PACIENTE", pac['nombre'])
            pdf.add_info("IDENTIFICACIÓN", f"Nacimiento: {pac['f_nac']} | Edad: {pac['edad']} | Sexo: {pac['sexo']}")
            pdf.add_info("SOMATOMETRÍA", f"Peso: {pac['peso']} kg | Talla: {pac['talla']} cm")
            pdf.add_info("SIGNOS VITALES", f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | T: {pac['temp']}°C")
            pdf.section_header("2. ANTECEDENTES")
            pdf.add_info("HEREDOFAMILIARES", pac['ahf']); pdf.add_info("PRENATALES", pac['prenatales']); pdf.add_info("NATALES", pac['natales'])
            pdf.add_info("VACUNAS", pac['vacunas']); pdf.add_info("ALIMENTACIÓN", pac['alimentacion']); pdf.add_info("DESARROLLO", pac['desarrollo'])
            pdf.section_header("3. PADECIMIENTO ACTUAL Y SISTEMAS")
            pdf.add_info("MOTIVO", pac['motivo']); pdf.add_info("DIGESTIVO", pac['as_digestivo']); pdf.add_info
