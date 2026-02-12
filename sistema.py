import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io
# 1. IMPORTA LAS FUNCIONES DE TU ARCHIVO interface_premium.py
from interface_premium import cargar_estilo_hospital

# Configuración de página - DEBE SER LO PRIMERO
st.set_page_config(page_title="Gestión Hospitalaria Pediátrica", layout="wide", page_icon="🏥")

# Aplicar el estilo visual (Colores, sombras y fuentes)
cargar_estilo_hospital()

# --- MOTOR DE PDF ---
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
        self.write(6, f"{str(value)}\n")

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} - Confidencialidad Médica', 0, 0, 'C')

# --- GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    if "password_correct" not in st.session_state:
        # Pantalla de inicio de sesión elegante
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            with st.container(border=True):
                st.title("🏥 Acceso Clínico")
                choice = st.radio("Acción", ["Iniciar Sesión", "Registrarse"], horizontal=True)
                if choice == "Iniciar Sesión":
                    u = st.text_input("Usuario")
                    p = st.text_input("Contraseña", type="password")
                    if st.button("Ingresar", use_container_width=True, type="primary"):
                        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                            st.session_state["password_correct"] = True
                            st.session_state["user_actual"] = u
                            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                            st.rerun()
                        else: st.error("Acceso denegado")
                else:
                    nu = st.text_input("Nuevo Usuario")
                    np = st.text_input("Contraseña", type="password")
                    if st.button("Crear Cuenta", use_container_width=True):
                        st.session_state["db_usuarios"][nu] = np
                        st.success("Usuario creado")
        return False
    return True

# --- APP PRINCIPAL ---
if login_registro():
    # SIDEBAR ÚNICO Y ORGANIZADO
    with st.sidebar:
        st.markdown(f"### 🩺 Dr(a). {st.session_state['user_actual']}")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            del st.session_state["password_correct"]
            st.rerun()
        
        st.divider()
        if st.button("➕ NUEVO PACIENTE", type="primary", use_container_width=True):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "tipo_interrogatorio": "Directo", "informante": "", "parentesco": "",
                "telefono": "", "domicilio": "", "originario": "", "residente": "", "religion": "",
                "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
                "fc": "", "fr": "", "sat": "", "temp": "", "ta": "", "glu": "", "peso": "", "talla": "",
                "ahf": "", "vacunas": "", "prenatales": "", "alimentacion": "", "natales": "", 
                "apgar": "", "silverman": "", "desarrollo": "", "patologicos": "", 
                "motivo": "", "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "", 
                "as_urinario": "", "as_piel": "", "as_musculo": "", "exploracion": "", 
                "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()
        
        lista_p = list(st.session_state["lista_pacientes"].keys())
        if lista_p:
            st.session_state["paciente_seleccionado"] = st.selectbox("📂 Expediente:", lista_p)
            st.divider()
            if st.button("📊 Generar Resumen de Turno", use_container_width=True):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_title("Resumen General de Guardia")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.add_field("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                    pdf_r.add_field("DIAGNÓSTICO", pdata['dx'])
                    pdf_r.ln(2)
                st.download_button("📥 Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen_Turno.pdf", use_container_width=True)

    # CUERPO DE LA APP
    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        
        st.title(f"👤 {pac['nombre'] if pac['nombre'] else 'Nuevo Registro'}")
        
        t = st.tabs(["📋 Filiación", "🧬 Antecedentes", "🫁 Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with t[0]: 
            with st.container(border=True):
                st.subheader("Datos de Filiación")
                pac['nombre'] = st.text_input("Nombre Completo del Paciente:", value=pac['nombre'])
                c1, c2, c3 = st.columns(3)
                pac['f_nac'] = c1.date_input("Fecha de Nacimiento:", pac['f_nac'])
                pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
                pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
                
                st.divider()
                c4, c5, c6 = st.columns(3)
                pac['tipo_interrogatorio'] = c4.selectbox("Tipo de Interrogatorio:", ["Directo", "Indirecto", "Mixto"])
                pac['informante'] = c5.text_input("Nombre del Informante:", value=pac['informante'])
                pac['parentesco'] = c6.text_input("Parentesco/Relación:", value=pac['parentesco'])
                
                st.divider()
                c7, c8 = st.columns(2)
                pac['telefono'] = c7.text_input("Teléfono:", value=pac['telefono'])
                pac['religion'] = c8.text_input("Religión:", value=pac['religion'])
                pac['domicilio'] = st.text_input("Domicilio Completo:", value=pac['domicilio'])
                
                col_or, col_res = st.columns(2)
                pac['originario'] = col_or.text_input("Originario de:", value=pac['originario'])
                pac['residente'] = col_res.text_input("Residente de:", value=pac['residente'])

            with st.container(border=True):
                st.subheader("Signos Vitales y Somatometría")
                s1, s2, s3, s4 = st.columns(4)
                pac['fc'] = s1.text_input("FC (lpm):", value=pac['fc'])
                pac['fr'] = s2.text_input("FR (rpm):", value=pac['fr'])
                pac['sat'] = s3.text_input("SatO2 (%):", value=pac['sat'])
                pac['temp'] = s4.text_input("Temp (°C):", value=pac['temp'])
                
                s5, s6, s7, s8 = st.columns(4)
                pac['ta'] = s5.text_input("TA (mmHg):", value=pac['ta'])
                pac['glu'] = s6.text_input("Glucosa (mg/dL):", value=pac['glu'])
                pac['peso'] = s7.text_input("Peso (kg):", value=pac['peso'])
                pac['talla'] = s8.text_input("Talla (cm):", value=pac['talla'])

        with t[1]: 
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    pac['ahf'] = st.text_area("Heredofamiliares:", value=pac['ahf'], height=100)
                    pac['prenatales'] = st.text_area("Prenatales:", value=pac['prenatales'], height=100)
                    pac['natales'] = st.text_area("Natales (Parto):", value=pac['natales'], height=100)
                with c2:
                    pac['vacunas'] = st.text_area("Vacunas / Tamiz:", value=pac['vacunas'], height=100)
                    pac['alimentacion'] = st.text_area("Alimentación:", value=pac['alimentacion'], height=100)
                    pac['desarrollo'] = st.text_area("Hitos Desarrollo:", value=pac['desarrollo'], height=100)
                
                st.divider()
                c3, c4 = st.columns(2)
                pac['apgar'] = c3.text_input("APGAR:", value=pac['apgar'])
                pac['silverman'] = c4.text_input("Silverman:", value=pac['silverman'])
                pac['patologicos'] = st.text_area("Antecedentes Patológicos (Alergias, Qx, Transfusionales):", value=pac['patologicos'])

        with t[2]: 
            with st.container(border=True):
                pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'], height=150)
                st.divider()
                a1, a2 = st.columns(2)
                pac['as_digestivo'] = a1.text_area("A. Digestivo:", value=pac['as_digestivo'])
                pac['as_resp'] = a2.text_area("A. Respiratorio:", value=pac['as_resp'])
                pac['as_cardio'] = a1.text_area("A. Cardiovascular:", value=pac['as_cardio'])
                pac['as_neuro'] = a2.text_area("A. Neurológico:", value=pac['as_neuro'])
                pac['as_urinario'] = a1.text_area("A. Genitourinario:", value=pac['as_urinario'])
                pac['as_piel'] = a2.text_area("Piel y Faneras:", value=pac['as_piel'])
                pac['as_musculo'] = st.text_area("Músculo-Esquelético:", value=pac['as_musculo'])

        with t[3]: 
            with st.container(border=True):
                pac['exploracion'] = st.text_area("Exploración Física Cefalo-Caudal:", value=pac['exploracion'], height=400)

        with t[4]: 
            with st.container(border=True):
                pac['dx'] = st.text_area("Impresión Diagnóstica:", value=pac['dx'], height=150)
                pac['plan'] = st.text_area("Plan de Manejo:", value=pac['plan'], height=200)
                
                if st.button("🖨️ GENERAR HISTORIA CLINICA COMPLETA", type="primary", use_container_width=True):
                    pdf = PEDIATRIC_PDF()
                    pdf.add_page()
                    # (Aquí va toda tu lógica de mapeo de PDF que ya tenías)
                    pdf.section_title("1. Datos de Filiación")
                    pdf.add_field("Paciente", pac['nombre'])
                    pdf.add_field("Edad / Sexo", f"{pac['edad']} / {pac['sexo']}")
                    pdf.section_title("2. Signos Vitales")
                    pdf.add_field("Vitales", f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | Temp: {pac['temp']}")
                    pdf.section_title("Diagnóstico")
                    pdf.add_field("DX", pac['dx'])
                    pdf.add_field("Plan", pac['plan'])
                    
                    st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf", use_container_width=True)

        with t[5]: 
            with st.container(border=True):
                st.subheader("Seguimiento del Paciente")
                nueva = st.text_area("Escribir nueva nota de evolución:")
                if st.button("💾 Guardar Nota", use_container_width=True):
                    if nueva:
                        pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                        st.rerun()
                
                st.divider()
                for n in pac["notas_evolucion"]:
                    st.info(f"📅 {n['f']}\n{n['t']}")
