import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io
import json
import os
from interface_premium import cargar_estilo_hospital

# --- CONFIGURACIÓN ---
NOMBRE_APP = "Unidad Pediátrica" 
st.set_page_config(page_title=NOMBRE_APP, layout="wide", page_icon="🏥")
cargar_estilo_hospital()

# --- MOTOR PDF MEJORADO ---
class CLINIC_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(0, 51, 102)
        # Usamos los datos del encabezado definidos por el usuario
        encabezado = st.session_state.get("datos_medico", "Centro Médico Pediátrico")
        self.cell(0, 10, encabezado.upper(), 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, st.session_state.get("sub_encabezado", ""), 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(0, 51, 102)
        self.line(10, 30, 200, 30)

    def section_title(self, txt):
        self.ln(5)
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(235, 245, 255)
        self.cell(0, 7, f" {txt}", 0, 1, 'L', fill=True)
        self.ln(2)

    def add_field(self, label, value):
        self.set_font('Arial', 'B', 9)
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 6, str(value) if value else "No referido")

# --- INICIALIZACIÓN DE ESTADO ---
if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
if "datos_medico" not in st.session_state: st.session_state["datos_medico"] = "Dr. Dario Monjaras"
if "sub_encabezado" not in st.session_state: st.session_state["sub_encabezado"] = "Cédula Profesional: 1234567 | Pediatría Especializada"

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Configuración")
    st.session_state["datos_medico"] = st.text_input("Nombre en Encabezados:", st.session_state["datos_medico"])
    st.session_state["sub_encabezado"] = st.text_area("Sub-encabezado (Cédula/Dirección):", st.session_state["sub_encabezado"])
    st.divider()
    if st.button("➕ NUEVO PACIENTE", type="primary"):
        p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
        st.session_state["lista_pacientes"][p_id] = {
            "nombre": "", "f_nac": date(2020,1,1), "edad": "", "sexo": "M",
            "fc": "", "fr": "", "sat": "", "temp": "",
            "ahf": "", "prenatales": "", "natales": "", "vacunas": "", "desarrollo": "",
            "motivo": "", "as_digestivo": "", "as_cardio": "", "as_urinario": "", "as_resp": "",
            "exploracion": "", "dx": "", "plan": "", "receta": ""
        }
        st.session_state["paciente_actual"] = p_id
        st.rerun()
    
    opciones = list(st.session_state["lista_pacientes"].keys())
    if opciones:
        st.session_state["paciente_actual"] = st.selectbox("Expediente:", opciones)

# --- CUERPO PRINCIPAL ---
if "paciente_actual" in st.session_state:
    pac = st.session_state["lista_pacientes"][st.session_state["paciente_actual"]]
    st.header(f"📋 Paciente: {pac['nombre'] if pac['nombre'] else 'Nuevo'}")
    
    t = st.tabs(["Filiación", "Antecedentes", "Sistemas", "Exploración", "Diagnóstico", "Receta", "Evolución"])

    with t[0]: # FILIACIÓN
        pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
        c1, c2, c3 = st.columns(3)
        pac['f_nac'] = c1.date_input("Nacimiento:", pac['f_nac'])
        pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
        pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
        st.subheader("Signos Vitales")
        s1, s2, s3, s4 = st.columns(4)
        pac['fc'], pac['fr'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr'])
        pac['sat'], pac['temp'] = s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])

    with t[1]: # ANTECEDENTES
        pac['ahf'] = st.text_area("Heredofamiliares:", value=pac['ahf'])
        pac['prenatales'] = st.text_area("Prenatales:", value=pac['prenatales'])
        pac['natales'] = st.text_area("Natales:", value=pac['natales'])
        pac['vacunas'] = st.text_area("Vacunas:", value=pac['vacunas'])
        pac['desarrollo'] = st.text_area("Hitos del Desarrollo:", value=pac['desarrollo'])

    with t[2]: # SISTEMAS
        pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'])
        col_a, col_b = st.columns(2)
        pac['as_digestivo'] = col_a.text_area("A. Digestivo:", value=pac['as_digestivo'])
        pac['as_resp'] = col_b.text_area("A. Respiratorio:", value=pac['as_resp'])
        pac['as_cardio'] = col_a.text_area("A. Cardiovascular:", value=pac['as_cardio'])
        pac['as_urinario'] = col_b.text_area("A. Genitourinario:", value=pac['as_urinario'])

    with t[3]: # EXPLORACIÓN
        pac['exploracion'] = st.text_area("Exploración Física:", value=pac['exploracion'], height=250)

    with t[4]: # DX Y PLAN
        pac['dx'] = st.text_area("Diagnóstico:", value=pac['dx'])
        pac['plan'] = st.text_area("Plan de Manejo:", value=pac['plan'])
        
        if st.button("🖨️ Generar Historia Clínica Completa", use_container_width=True):
            pdf = CLINIC_PDF()
            pdf.add_page()
            pdf.section_title("DATOS DE FILIACIÓN")
            pdf.add_field("Nombre", pac['nombre'])
            pdf.add_field("Edad/Sexo", f"{pac['edad']} / {pac['sexo']}")
            pdf.add_field("Signos", f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | T: {pac['temp']}°C")
            pdf.section_title("ANTECEDENTES")
            pdf.add_field("Heredofamiliares", pac['ahf'])
            pdf.add_field("Prenatales/Natales", f"{pac['prenatales']}\n{pac['natales']}")
            pdf.section_title("PADECIMIENTO Y SISTEMAS")
            pdf.add_field("Actual", pac['motivo'])
            pdf.add_field("Exploración", pac['exploracion'])
            pdf.section_title("CONCLUSIÓN")
            pdf.add_field("DX", pac['dx'])
            pdf.add_field("PLAN", pac['plan'])
            st.download_button("📥 Descargar Historia", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

    with t[5]: # RECETA EDITABLE
        st.info("El encabezado de la receta se edita en la barra lateral izquierda.")
        pac['receta'] = st.text_area("Instrucciones de la Receta:", value=pac['receta'], height=300)
        if st.button("💊 Generar Receta PDF", use_container_width=True):
            r_pdf = CLINIC_PDF()
            r_pdf.add_page()
            r_pdf.ln(10)
            r_pdf.set_font("Arial", "B", 11)
            r_pdf.cell(0, 10, f"PACIENTE: {pac['nombre']}", 0, 1)
            r_pdf.set_font("Arial", "", 11)
            r_pdf.multi_cell(0, 8, pac['receta'])
            st.download_button("📥 Descargar Receta", r_pdf.output(dest='S').encode('latin-1'), f"Receta_{pac['nombre']}.pdf")

    with t[6]: # EVOLUCIÓN (DESCARGA SIN GUARDAR)
        st.subheader("Nueva Nota de Evolución")
        nota_temp = st.text_area("Escriba la nota de hoy:", height=200, placeholder="Paciente estable...")
        if st.button("📄 Generar Nota de Evolución (PDF Directo)"):
            if nota_temp:
                e_pdf = CLINIC_PDF()
                e_pdf.add_page()
                e_pdf.section_title(f"NOTA DE EVOLUCIÓN - {datetime.now().strftime('%d/%m/%Y')}")
                e_pdf.add_field("Paciente", pac['nombre'])
                e_pdf.add_field("Signos", f"FC: {pac['fc']} | FR: {pac['fr']} | T: {pac['temp']}°C")
                e_pdf.ln(5)
                e_pdf.set_font("Arial", "", 11)
                e_pdf.multi_cell(0, 8, nota_temp)
                st.download_button("📥 Descargar Nota Actual", e_pdf.output(dest='S').encode('latin-1'), "Nota_Evolucion.pdf")
            else:
                st.warning("Escriba algo en la nota antes de generar el PDF.")
