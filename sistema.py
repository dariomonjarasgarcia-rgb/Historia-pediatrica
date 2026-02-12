import streamlit as st
# 1. IMPORTA LAS FUNCIONES QUE ACABAMOS DE CREAR
from interface_premium import cargar_estilo_hospital, render_sidebar_hospital

# 2. APLICA EL ESTILO (Ponlo justo después de los imports)
cargar_estilo_hospital()

# 3. DIBUJA EL SIDEBAR
render_sidebar_hospital("Dr(a). D")
import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. MOTOR DE PDF CON ESTILO MÉDICO PROFESIONAL ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102) # Azul Médico
        self.cell(0, 10, 'EXPEDIENTE CLINICO PEDIATRICO', 0, 1, 'C')
        self.set_draw_color(0, 51, 102)
        self.line(10, 22, 200, 22)
        self.ln(8)

    def section_title(self, txt):
        self.ln(2)
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 243, 255) # Celeste suave
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
        self.cell(0, 10, f'Página {self.page_no()} - Confidencialidad Médica Garantizada', 0, 0, 'C')

# --- 2. GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    if "password_correct" not in st.session_state:
        st.title("🏥 Gestión Hospitalaria Pediátrica")
        menu = ["Iniciar Sesión", "Registrarse"]
        choice = st.radio("Acceso", menu, horizontal=True)
        if choice == "Iniciar Sesión":
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                    st.session_state["password_correct"] = True
                    st.session_state["user_actual"] = u
                    if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                    st.rerun()
                else: st.error("Acceso denegado")
        else:
            nu = st.text_input("Nuevo Usuario")
            np = st.text_input("Contraseña", type="password")
            if st.button("Crear Cuenta"):
                st.session_state["db_usuarios"][nu] = np
                st.success("Usuario creado")
        return False
    return True

# --- 3. APP PRINCIPAL ---
if login_registro():
    with st.sidebar:
        st.write(f"🩺 Dr(a). **{st.session_state['user_actual']}**")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        if st.button("➕ NUEVO PACIENTE"):
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
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista_p)
            st.divider()
            # BOTÓN DE RESUMEN DE TURNO RECUPERADO
            if st.button("📊 Generar Resumen de Turno"):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_title("Resumen General de Guardia")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.add_field("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                    pdf_r.add_field("DIAGNÓSTICO", pdata['dx'])
                    pdf_r.ln(2)
                st.download_button("Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen_Turno.pdf")

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.header(f"🧑‍⚕️ {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")

        t = st.tabs(["Filiación/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]: 
            st.subheader("Datos de Filiación")
            pac['nombre'] = st.text_input("Nombre Completo del Paciente:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'] = c1.date_input("Fecha de Nacimiento:", pac['f_nac'])
            pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
            pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
            
            st.divider()
            c4, c5, c6 = st.columns(3)
            pac['tipo_interrogatorio'] = c4.selectbox("Tipo de Interrogatorio:", ["Directo", "Indirecto", "Mixto"])
            pac['informante'] = c5.text_input("Nombre del Informante (si aplica):", value=pac['informante'])
            pac['parentesco'] = c6.text_input("Parentesco/Relación:", value=pac['parentesco'])
            
            st.divider()
            c7, c8, c9 = st.columns(3)
            pac['telefono'] = c7.text_input("Teléfono:", value=pac['telefono'])
            pac['religion'] = c8.text_input("Religión:", value=pac['religion'])
            pac['domicilio'] = st.text_input("Domicilio:", value=pac['domicilio'])
            
            col_or, col_res = st.columns(2)
            pac['originario'] = col_or.text_input("Originario de:", value=pac['originario'])
            pac['residente'] = col_res.text_input("Residente de:", value=pac['residente'])

            st.subheader("Signos Vitales y Somatometría")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", value=pac['fc']), s2.text_input("FR:", value=pac['fr']), s3.text_input("SatO2:", value=pac['sat']), s4.text_input("Temp:", value=pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", value=pac['ta']), s6.text_input("Glucosa:", value=pac['glu']), s7.text_input("Peso (kg):", value=pac['peso']), s8.text_input("Talla (cm):", value=pac['talla'])

        with t[1]: # ANTECEDENTES (3 COLUMNAS)
            c1, c2, c3 = st.columns(3)
            pac['ahf'] = c1.text_area("Heredofamiliares:", value=pac['ahf'])
            pac['vacunas'] = c1.text_area("Vacunas / Tamiz:", value=pac['vacunas'])
            pac['prenatales'] = c2.text_area("Prenatales:", value=pac['prenatales'])
            pac['alimentacion'] = c2.text_area("Alimentación:", value=pac['alimentacion'])
            pac['natales'] = c3.text_area("Natales (Parto):", value=pac['natales'])
            pac['apgar'] = c3.text_input("APGAR:", value=pac['apgar'])
            pac['silverman'] = c3.text_input("Silverman:", value=pac['silverman'])
            pac['desarrollo'] = c3.text_area("Hitos Desarrollo:", value=pac['desarrollo'])
            pac['patologicos'] = st.text_area("Antecedentes Patológicos (Alergias, Qx, Transfusionales):", value=pac['patologicos'])

        with t[2]: # INTERROGATORIO POR SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("A. Digestivo:", value=pac['as_digestivo']), a2.text_area("A. Respiratorio:", value=pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("A. Cardiovascular:", value=pac['as_cardio']), a2.text_area("A. Neurológico:", value=pac['as_neuro'])
            pac['as_urinario'], pac['as_piel'] = a1.text_area("A. Genitourinario:", value=pac['as_urinario']), a2.text_area("Piel y Faneras:", value=pac['as_piel'])
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:", value=pac['as_musculo'])

        with t[3]: # EXPLORACIÓN
            pac['exploracion'] = st.text_area("Exploración Física Cefalo-Caudal:", value=pac['exploracion'], height=300)

        with t[4]: # DX Y PLAN CON VACIADO COMPLETO
            pac['dx'] = st.text_area("Impresión Diagnóstica:", value=pac['dx'], height=150)
            pac['plan'] = st.text_area("Plan de Manejo:", value=pac['plan'], height=200)
            
            if st.button("🖨️ GENERAR HISTORIA CLINICA COMPLETA"):
                pdf = PEDIATRIC_PDF()
                pdf.add_page()
                
                # SECCIÓN 1: FILIACIÓN (MAPEO COMPLETO)
                pdf.section_title("1. Datos de Filiación e Interrogatorio")
                pdf.add_field("Paciente", pac['nombre'])
                pdf.add_field("Edad / Sexo", f"{pac['edad']} / {pac['sexo']}")
                pdf.add_field("Interrogatorio", f"{pac['tipo_interrogatorio']} (Informante: {pac['informante']} - {pac['parentesco']})")
                pdf.add_field("Ubicación", f"Origen: {pac['originario']} | Residente: {pac['residente']}")
                pdf.add_field("Contacto/Religión", f"Tel: {pac['telefono']} | Religión: {pac['religion']}")
                
                # SECCIÓN 2: SIGNOS (MAPEO COMPLETO)
                pdf.section_title("2. Signos Vitales y Somatometría")
                pdf.add_field("Vitales", f"FC: {pac['fc']} | FR: {pac['fr']} | Sat: {pac['sat']} | Temp: {pac['temp']} | TA: {pac['ta']}")
                pdf.add_field("Somatometría", f"Peso: {pac['peso']} kg | Talla: {pac['talla']} cm | Glu: {pac['glu']} mg/dL")
                
                # SECCIÓN 3: ANTECEDENTES (MAPEO COMPLETO)
                pdf.section_title("3. Antecedentes")
                pdf.add_field("Hereditarios", pac['ahf'])
                pdf.add_field("Prenatales/Alimentación", f"{pac['prenatales']} | {pac['alimentacion']}")
                pdf.add_field("Perinatales", f"Parto: {pac['natales']} | APGAR: {pac['apgar']} | SV: {pac['silverman']}")
                pdf.add_field("Desarrollo/Vacunas", f"Hitos: {pac['desarrollo']} | Vacunas: {pac['vacunas']}")
                pdf.add_field("Patológicos", pac['patologicos'])
                
                # SECCIÓN 4: PADECIMIENTO Y SISTEMAS (MAPEO COMPLETO)
                pdf.section_title("4. Interrogatorio por Sistemas")
                pdf.add_field("Padecimiento Actual", pac['motivo'])
                pdf.add_field("Sistemas", f"Digestivo: {pac['as_digestivo']} | Resp: {pac['as_resp']} | Cardio: {pac['as_cardio']} | Neuro: {pac['as_neuro']} | Genitourinario: {pac['as_urinario']} | Piel: {pac['as_piel']} | Musculoesq: {pac['as_musculo']}")
                
                # SECCIÓN 5: EXPLORACIÓN (MAPEO COMPLETO)
                pdf.section_title("5. Exploración Física")
                pdf.add_field("Hallazgos", pac['exploracion'])
                
                # SECCIÓN 6: DX Y PLAN (MAPEO COMPLETO)
                pdf.section_title("6. Diagnóstico y Plan")
                pdf.add_field("Impresión Diagnóstica", pac['dx'])
                pdf.add_field("Plan de Manejo", pac['plan'])
                
                st.download_button("Descargar Historia Clínica", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]: # EVOLUCIÓN
            st.subheader("Seguimiento del Paciente")
            nueva = st.text_area("Escribir nota de evolución:")
            if st.button("💾 Guardar Nota"):
                if nueva:
                    pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            
            if pac["notas_evolucion"] and st.button("📄 GENERAR PDF DE NOTAS"):
                pdf_e = PEDIATRIC_PDF()
                pdf_e.add_page()
                pdf_e.section_title(f"HISTORIAL DE EVOLUCION: {pac['nombre']}")
                for n in pac["notas_evolucion"]:
                    pdf_e.set_font('Arial', 'B', 10)
                    pdf_e.cell(0, 7, f"Fecha: {n['f']}", 0, 1)
                    pdf_e.set_font('Arial', '', 10)
                    pdf_e.multi_cell(0, 6, n['t'])
                    pdf_e.ln(4)
                    pdf_e.line(10, pdf_e.get_y(), 200, pdf_e.get_y())
                st.download_button("Descargar Notas", pdf_e.output(dest='S').encode('latin-1'), f"Evolucion_{pac['nombre']}.pdf")
            
            for n in pac["notas_evolucion"]:
                st.info(f"📅 {n['f']}\n{n['t']}")


