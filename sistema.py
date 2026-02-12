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

# --- PERSISTENCIA USUARIOS ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f: return json.load(f)
    return {"admin": "medico2026"}

def guardar_usuario(u, p):
    db = cargar_usuarios()
    db[u] = p
    with open("usuarios.json", "w") as f: json.dump(db, f)

# --- MOTOR PDF PROFESIONAL ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102) 
        self.cell(0, 10, 'EXPEDIENTE CLINICO PEDIATRICO', 0, 1, 'C')
        self.set_draw_color(0, 51, 102)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def section_title(self, txt):
        self.ln(2)
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 243, 255) 
        self.set_text_color(0, 51, 102)
        self.cell(0, 7, f"  {txt.upper()}", 0, 1, 'L', fill=True)
        self.ln(2)

    def add_field(self, label, value):
        self.set_font('Arial', 'B', 9)
        self.set_text_color(50, 50, 50)
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        val = str(value) if value else "No referido"
        self.multi_cell(0, 6, val)
        self.ln(1)

class RECETA_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, NOMBRE_APP.upper(), 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, "Cédula Profesional: XXXX-XXXX | Institución: Universidad Ejemplo", 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(0, 51, 102)
        self.line(10, 28, 200, 28)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, '__________________________________________', 0, 1, 'C')
        self.cell(0, 5, f'Firma del Médico: {st.session_state.get("user_actual", "Médico")}', 0, 0, 'C')

# --- LOGIN ---
def login_registro():
    if "db_usuarios" not in st.session_state: st.session_state["db_usuarios"] = cargar_usuarios()
    if "password_correct" not in st.session_state:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.container(border=True):
                st.title("📂 Expediente Médico")
                choice = st.radio("Acceso", ["Iniciar Sesión", "Registrarse"], horizontal=True)
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                if choice == "Iniciar Sesión":
                    if st.button("🚀 Ingresar", use_container_width=True, type="primary"):
                        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                            st.session_state["password_correct"], st.session_state["user_actual"] = True, u
                            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                            st.rerun()
                        else: st.error("Error de acceso")
                else:
                    if st.button("➕ Crear Cuenta", use_container_width=True):
                        guardar_usuario(u, p)
                        st.session_state["db_usuarios"] = cargar_usuarios()
                        st.success("Usuario creado")
        return False
    return True

# --- MAIN APP ---
if login_registro():
    with st.sidebar:
        st.markdown(f"### 🏥 {NOMBRE_APP}")
        st.write(f"🩺 Dr(a). **{st.session_state['user_actual']}**")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            del st.session_state["password_correct"]; st.rerun()
        st.divider()
        if st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "tipo_interrogatorio": "Directo", "informante": "", "parentesco": "",
                "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
                "fc": "", "fr": "", "sat": "", "temp": "", "ahf": "", "prenatales": "", 
                "natales": "", "vacunas": "", "alimentacion": "", "desarrollo": "", 
                "patologicos": "", "motivo": "", "as_digestivo": "", "as_cardio": "", 
                "as_urinario": "", "as_resp": "", "as_neuro": "", "as_piel": "", 
                "as_musculo": "", "exploracion": "", "dx": "", "plan": "", 
                "notas_evolucion": [], "receta_texto": ""
            }
            st.session_state["paciente_seleccionado"] = p_id; st.rerun()
        
        lista_p = list(st.session_state["lista_pacientes"].keys())
        if lista_p:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista_p)

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.header(f"🧑‍⚕️ {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")

        t = st.tabs(["📋 Filiación", "🧬 Antecedentes", "🫁 Sistemas", "🔍 Exploración", "📝 DX/Plan", "💊 Receta", "📈 Evolución"])

        with t[0]: # FILIACIÓN
            with st.container(border=True):
                st.subheader("Datos de Filiación")
                pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
                c1, c2, c3 = st.columns(3)
                pac['f_nac'], pac['edad'], pac['sexo'] = c1.date_input("Nacimiento:", pac['f_nac']), c2.text_input("Edad:", value=pac['edad']), c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
                st.divider()
                c4, c5, c6 = st.columns(3)
                pac['tipo_interrogatorio'] = c4.selectbox("Interrogatorio:", ["Directo", "Indirecto", "Mixto"])
                pac['informante'] = c5.text_input("Informante:", value=pac['informante'])
                pac['parentesco'] = c6.text_input("Relación:", value=pac['parentesco'])
            with st.container(border=True):
                st.subheader("Signos Vitales")
                s1, s2, s3, s4 = st.columns(4)
                pac['fc'], pac['fr'] = s1.text_input("FC:", value=pac['fc']), s2.text_input("FR:", value=pac['fr'])
                pac['sat'], pac['temp'] = s3.text_input("SatO2:", value=pac['sat']), s4.text_input("Temp:", value=pac['temp'])

        with t[1]: # ANTECEDENTES
            with st.container(border=True):
                st.subheader("Antecedentes del Paciente")
                pac['ahf'] = st.text_area("Heredofamiliares:", value=pac['ahf'], height=100)
                pac['prenatales'] = st.text_area("Prenatales:", value=pac['prenatales'], height=100)
                pac['natales'] = st.text_area("Natales (Parto):", value=pac['natales'], height=100)
                pac['vacunas'] = st.text_area("Vacunas:", value=pac['vacunas'], height=100)
                pac['desarrollo'] = st.text_area("Hitos Desarrollo:", value=pac['desarrollo'], height=100)
                pac['patologicos'] = st.text_area("Patológicos/Alergias:", value=pac['patologicos'], height=100)

        with t[2]: # SISTEMAS
            with st.container(border=True):
                pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'], height=120)
                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    pac['as_digestivo'] = st.text_area("A. Digestivo:", value=pac['as_digestivo'], height=100)
                    pac['as_cardio'] = st.text_area("A. Cardiovascular:", value=pac['as_cardio'], height=100)
                    pac['as_urinario'] = st.text_area("A. Genitourinario:", value=pac['as_urinario'], height=100)
                with col_b:
                    pac['as_resp'] = st.text_area("A. Respiratorio:", value=pac['as_resp'], height=100)
                    pac['as_neuro'] = st.text_area("A. Neurológico:", value=pac['as_neuro'], height=100)
                    pac['as_piel'] = st.text_area("Piel y Faneras:", value=pac['as_piel'], height=100)

        with t[3]: # EXPLORACIÓN
            with st.container(border=True):
                pac['exploracion'] = st.text_area("Exploración Física:", value=pac['exploracion'], height=300)

        with t[4]: # DX/PLAN
            with st.container(border=True):
                pac['dx'] = st.text_area("Impresión Diagnóstica:", value=pac['dx'], height=150)
                pac['plan'] = st.text_area("Plan de Manejo:", value=pac['plan'], height=150)
                
                if st.button("🖨️ GENERAR HISTORIA COMPLETA", type="primary", use_container_width=True):
                    pdf = PEDIATRIC_PDF()
                    pdf.add_page()
                    pdf.section_title("Datos de Filiación")
                    pdf.add_field("Paciente", pac['nombre'])
                    pdf.add_field("Edad/Sexo", f"{pac['edad']} / {pac['sexo']}")
                    pdf.section_title("Signos Vitales")
                    pdf.add_field("Signos", f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | Temp: {pac['temp']}")
                    pdf.section_title("Diagnóstico y Plan")
                    pdf.add_field("DX", pac['dx'])
                    pdf.add_field("PLAN", pac['plan'])
                    st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]: # RECETA
            with st.container(border=True):
                st.subheader("💊 Receta")
                pac['receta_texto'] = st.text_area("Tratamiento:", value=pac['receta_texto'], height=200)
                if st.button("📄 GENERAR RECETA", type="primary", use_container_width=True):
                    r_pdf = RECETA_PDF()
                    r_pdf.add_page()
                    r_pdf.set_font('Arial', 'B', 10)
                    r_pdf.cell(100, 7, f"PACIENTE: {pac['nombre']}")
                    r_pdf.cell(0, 7, f"FECHA: {date.today()}", 0, 1, 'R')
                    r_pdf.ln(5)
                    r_pdf.set_font('Arial', '', 11)
                    r_pdf.multi_cell(0, 8, pac['receta_texto'])
                    st.download_button("📥 Descargar Receta", r_pdf.output(dest='S').encode('latin-1'), f"Receta_{pac['nombre']}.pdf")

        with t[6]: # EVOLUCIÓN
            with st.container(border=True):
                st.subheader("Notas de Evolución")
                nueva = st.text_area("Nueva nota médica:", placeholder="Escriba aquí...")
                if st.button("💾 Guardar Nota", use_container_width=True, type="primary"):
                    if nueva:
                        registro = {
                            "f": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                            "t": nueva,
                            "sv": f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | Temp: {pac['temp']}"
                        }
                        pac["notas_evolucion"].insert(0, registro)
                        st.rerun()
                
                st.divider()
                if pac["notas_evolucion"]:
                    if st.button("📄 GENERAR REPORTE DE EVOLUCIÓN", use_container_width=True):
                        pdf_ev = PEDIATRIC_PDF()
                        pdf_ev.add_page()
                        pdf_ev.section_title("Evolución Clínica")
                        for n in pac["notas_evolucion"]:
                            pdf_ev.set_font('Arial', 'B', 10)
                            pdf_ev.cell(0, 7, f"FE
