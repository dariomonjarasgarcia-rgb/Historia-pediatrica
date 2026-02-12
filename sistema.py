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

# --- MOTOR PDF CON ESTILO ---
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

# --- INICIALIZACIÓN ---
if "lista_pacientes" not in st.session_state:
    st.session_state["lista_pacientes"] = {}
if "datos_medico" not in st.session_state:
    st.session_state["datos_medico"] = "Dr. Dario Monjaras"
if "sub_encabezado" not in st.session_state:
    st.session_state["sub_encabezado"] = "Pediatra Neonatólogo | Cédula: 1234567"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Configuración Profesional")
    st.session_state["datos_medico"] = st.text_input("Nombre del Médico:", st.session_state["datos_medico"])
    st.session_state["sub_encabezado"] = st.text_area("Datos de contacto/Cédula:", st.session_state["sub_encabezado"])
    st.divider()
    
    if st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True):
        p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
        st.session_state["lista_pacientes"][p_id] = {
            "nombre": "", "f_nac": date(2020,1,1), "edad": "", "sexo": "M",
            "fc": "", "fr": "", "sat": "", "temp": "",
            "ahf": "", "prenatales": "", "natales": "", "vacunas": "", "alimentacion": "", "desarrollo": "",
            "motivo": "", "as_digestivo": "", "as_cardio": "", "as_urinario": "", "as_resp": "",
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

    with t[0]:
        with st.container(border=True):
            st.subheader("Datos de Identificación")
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'] = c1.date_input("Fecha de Nacimiento:", pac['f_nac'])
            pac['edad'] = c2.text_input("Edad Actual:", value=pac['edad'])
            pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
        
        with st.container(border=True):
            st.subheader("📊 Signos Vitales")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'] = s1.text_input("F.C. (lpm):", pac['fc'])
            pac['fr'] = s2.text_input("F.R. (rpm):", pac['fr'])
            pac['sat'] = s3.text_input("SatO2 (%):", pac['sat'])
            pac['temp'] = s4.text_input("Temp (°C):", pac['temp'])

    with t[1]:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            pac['ahf'] = col1.text_area("Heredofamiliares:", value=pac['ahf'], height=150)
            pac['prenatales'] = col2.text_area("Prenatales:", value=pac['prenatales'], height=150)
            pac['natales'] = col1.text_area("Natales:", value=pac['natales'], height=150)
            pac['vacunas'] = col2.text_area("Vacunas:", value=pac['vacunas'], height=150)
            pac['alimentacion'] = col1.text_area("Alimentación:", value=pac['alimentacion'])
            pac['desarrollo'] = col2.text_area("Hitos Desarrollo:", value=pac['desarrollo'])

    with t[2]:
        with st.container(border=True):
            pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'], height=150)
            st.divider()
            ca, cb = st.columns(2)
            pac['as_digestivo'] = ca.text_area("Digestivo:", value=pac['as_digestivo'])
            pac['as_resp'] = cb.text_area("Respiratorio:", value=pac['as_resp'])
            pac['as_cardio'] = ca.text_area("Cardiovascular:", value=pac['as_cardio'])
            pac['as_urinario'] = cb.text_area("Genitourinario:", value=pac['as_urinario'])

    with t[3]:
        pac['exploracion'] = st.text_area("Hallazgos de Exploración Física:", value=pac['exploracion'], height=350)

    with t[4]:
        with st.container(border=True):
            pac['dx'] = st.text_area("Impresión Diagnóstica:", value=pac['dx'], height=100)
            pac['plan'] = st.text_area("Plan Terapéutico:", value=pac['plan'], height=150)
        
        if st.button("🖨️ GENERAR EXPEDIENTE COMPLETO", type="primary", use_container_width=True):
            pdf = CLINIC_PDF()
            pdf.add_page()
            
            # SECCIÓN 1: FILIACIÓN
            pdf.section_header("1. DATOS DE FILIACIÓN Y SIGNOS")
            pdf.add_info("PACIENTE", pac['nombre'])
            pdf.add_info("DATOS", f"Fecha Nacimiento: {pac['f_nac']} | Edad: {pac['edad']} | Sexo: {pac['sexo']}")
            pdf.add_info("SIGNOS VITALES", f"FC: {pac['fc']} | FR: {pac['fr']} | SatO2: {pac['sat']} | Temp: {pac['temp']}°C")
            
            # SECCIÓN 2: ANTECEDENTES (Todos los campos)
            pdf.section_header("2. ANTECEDENTES")
            pdf.add_info("HEREDOFAMILIARES", pac['ahf'])
            pdf.add_info("PRENATALES", pac['prenatales'])
            pdf.add_info("NATALES", pac['natales'])
            pdf.add_info("VACUNAS", pac['vacunas'])
            pdf.add_info("ALIMENTACIÓN", pac['alimentacion'])
            pdf.add_info("DESARROLLO", pac['desarrollo'])
            
            # SECCIÓN 3: PADECIMIENTO Y SISTEMAS
            pdf.section_header("3. PADECIMIENTO ACTUAL Y SISTEMAS")
            pdf.add_info("MOTIVO DE CONSULTA", pac['motivo'])
            pdf.add_info("AP. DIGESTIVO", pac['as_digestivo'])
            pdf.add_info("AP. RESPIRATORIO", pac['as_resp'])
            pdf.add_info("AP. CARDIOVASCULAR", pac['as_cardio'])
            pdf.add_info("AP. GENITOURINARIO", pac['as_urinario'])
            
            # SECCIÓN 4: EXPLORACIÓN FÍSICA
            pdf.section_header("4. EXPLORACIÓN FÍSICA")
            pdf.add_info("DETALLE", pac['exploracion'])
            
            # SECCIÓN 5: DX Y PLAN
            pdf.section_header("5. IMPRESIÓN DIAGNÓSTICA Y PLAN")
            pdf.add_info("DIAGNÓSTICO", pac['dx'])
            pdf.add_info("PLAN DE MANEJO", pac['plan'])
            
            st.download_button("📥 Descargar Expediente Completo", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

    with t[5]:
        with st.container(border=True):
            pac['receta_texto'] = st.text_area("Indicaciones Médicas:", value=pac['receta_texto'], height=300)
            if st.button("📄 IMPRIMIR RECETA", type="primary", use_container_width=True):
                r_pdf = CLINIC_PDF()
                r_pdf.add_page()
                r_pdf.ln(10)
                r_pdf.section_header(f"RECETA MÉDICA - {date.today().strftime('%d/%m/%Y')}")
                r_pdf.add_info("PACIENTE", pac['nombre'])
                r_pdf.ln(5)
                r_pdf.set_font("Arial", "", 12)
                r_pdf.multi_cell(0, 10, pac['receta_texto'])
                st.download_button("📥 Descargar Receta", r_pdf.output(dest='S').encode('latin-1'), f"Receta_{pac['nombre']}.pdf")

    with t[6]:
        st.subheader("📝 Nota de Evolución Rápida")
        nota_hoy = st.text_area("Descripción de la evolución:", height=250, placeholder="Escriba aquí los cambios observados hoy...")
        if st.button("💾 GENERAR NOTA (PDF)", use_container_width=True):
            if nota_hoy:
                e_pdf = CLINIC_PDF()
                e_pdf.add_page()
                e_pdf.section_header(f"NOTA DE EVOLUCIÓN - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                e_pdf.add_info("PACIENTE", pac['nombre'])
                e_pdf.add_info("SIGNOS", f"FC: {pac['fc']} | FR: {pac['fr']} | T: {pac['temp']}°C")
                e_pdf.ln(5)
                e_pdf.set_font("Arial", "", 11)
                e_pdf.multi_cell(0, 9, nota_hoy)
                st.download_button("📥 Descargar Nota", e_pdf.output(dest='S').encode('latin-1'), f"Nota_{pac['nombre']}.pdf")
            else:
                st.error("Por favor escriba la nota antes de generar el PDF.")
