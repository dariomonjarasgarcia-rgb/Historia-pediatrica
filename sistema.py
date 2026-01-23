import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. MOTOR DE PDF ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'EXPEDIENTE CLINICO PEDIATRICO', 0, 1, 'C')
        self.ln(5)

    def section_title(self, txt):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f" {txt}", 0, 1, 'L', fill=True)
        self.ln(2)

    def add_field(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 10)
        self.write(6, f"{str(value)}\n")

# --- 2. GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    if "password_correct" not in st.session_state:
        st.title("🏥 Sistema de Gestión Pediátrica")
        menu = ["Iniciar Sesión", "Registrarse"]
        choice = st.radio("Acceso al Sistema", menu, horizontal=True)
        if choice == "Iniciar Sesión":
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("🚀 Ingresar"):
                if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                    st.session_state["password_correct"] = True
                    st.session_state["user_actual"] = u
                    if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                    st.rerun()
                else: st.error("❌ Usuario o contraseña incorrectos")
        else:
            nu = st.text_input("Definir Nuevo Usuario")
            np = st.text_input("Definir Nueva Contraseña", type="password")
            if st.button("✅ Crear Cuenta"):
                if nu and np:
                    st.session_state["db_usuarios"][nu] = np
                    st.success("✨ Cuenta creada.")
        return False
    return True

# --- 3. APLICACIÓN PRINCIPAL ---
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
                "nombre": "", "informante": "", "telefono": "", "domicilio": "",
                "originario": "", "residente": "", "religion": "", "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
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
            st.session_state["paciente_seleccionado"] = st.selectbox("Seleccionar Expediente:", lista_p)
            if st.button("📊 Generar Resumen de Turno"):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_title("RESUMEN DE GUARDIA")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.add_field("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                    pdf_r.add_field("DX", pdata['dx'])
                    pdf_r.ln(2)
                st.download_button("📥 Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen_Turno.pdf")

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.header(f"🧒 Expediente: {pac['nombre'] if pac['nombre'] else 'Nuevo'}")

        t = st.tabs(["ID/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]: # FILIACIÓN + SIGNOS + SOMATOMETRÍA
            st.subheader("Ficha de Identificación")
            pac['nombre'] = st.text_input("Nombre Completo del Paciente:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['informante'], pac['telefono'], pac['religion'] = c1.text_input("Informante:", value=pac['informante']), c2.text_input("Teléfono:", value=pac['telefono']), c3.text_input("Religión:", value=pac['religion'])
            pac['domicilio'] = st.text_input("Domicilio Completo:", value=pac['domicilio'])
            c4, c5 = st.columns(2)
            pac['originario'], pac['residente'] = c4.text_input("Originario de:", value=pac['originario']), c5.text_input("Residente de:", value=pac['residente'])
            c6, c7, c8 = st.columns(3)
            pac['f_nac'], pac['edad'], pac['sexo'] = c6.date_input("F. Nacimiento:", pac['f_nac']), c7.text_input("Edad:", pac['edad']), c8.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
            
            st.divider()
            st.subheader("Signos Vitales y Somatometría")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr']), s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", pac['ta']), s6.text_input("Glucosa:", pac['glu']), s7.text_input("Peso (kg):", pac['peso']), s8.text_input("Talla (cm):", pac['talla'])

        with t[1]: # ANTECEDENTES (3 COLUMNAS)
            c1, c2, c3 = st.columns(3)
            pac['ahf'], pac['vacunas'] = c1.text_area("Heredofamiliares:", pac['ahf']), c1.text_area("Vacunas/Tamiz:", pac['vacunas'])
            pac['prenatales'], pac['alimentacion'] = c2.text_area("Prenatales:", pac['prenatales']), c2.text_area("Alimentación:", pac['alimentacion'])
            pac['natales'] = c3.text_area("Natales (Parto):", pac['natales'])
            pac['apgar'], pac['silverman'] = c3.text_input("APGAR:", pac['apgar']), c3.text_input("Silverman:", pac['silverman'])
            pac['desarrollo'] = c3.text_area("Hitos del Desarrollo:", pac['desarrollo'])
            pac['patologicos'] = st.text_area("Antecedentes Personales Patológicos (Alergias, Qx, etc):", pac['patologicos'])

        with t[2]: # SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:", pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("A. Digestivo:", pac['as_digestivo']), a2.text_area("A. Respiratorio:", pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("A. Cardiovascular:", pac['as_cardio']), a2.text_area("A. Neurológico:", pac['as_neuro'])
            pac['as_urinario'], pac['as_piel'] = a1.text_area("A. Genitourinario:", pac['as_urinario']), a2.text_area("Piel y Faneras:", pac['as_piel'])
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:", pac['as_musculo'])

        with t[3]: # EXPLORACIÓN
            pac['exploracion'] = st.text_area("Exploración Física:", pac['exploracion'], height=250)

        with t[4]: # DX Y PLAN
            pac['dx'] = st.text_area("Diagnóstico / Impresión Diagnóstica:", value=pac['dx'], height=150)
            pac['plan'] = st.text_area("Plan de Manejo y Tratamiento:", value=pac['plan'], height=200)
            if st.button("🖨️ Generar PDF Historia Clínica"):
                pdf = PEDIATRIC_PDF()
                pdf.add_page()
                pdf.section_title("1. IDENTIFICACION")
                pdf.add_field("Paciente", pac['nombre']); pdf.add_field("Edad", pac['edad']); pdf.add_field("Informante", pac['informante'])
                pdf.add_field("Origen/Residente", f"{pac['originario']} / {pac['residente']}"); pdf.add_field("Religion", pac['religion'])
                pdf.section_title("2. SIGNOS VITALES Y SOMATOMETRIA")
                pdf.add_field("Signos", f"FC:{pac['fc']} FR:{pac['fr']} Sat:{pac['sat']} T:{pac['temp']} TA:{pac['ta']}")
                pdf.add_field("Medidas", f"Peso:{pac['peso']} kg Talla:{pac['talla']} cm Glu:{pac['glu']}")
                pdf.section_title("3. ANTECEDENTES")
                pdf.add_field("Patologicos", pac['patologicos']); pdf.add_field("Natales", f"{pac['natales']} APGAR:{pac['apgar']}")
                pdf.section_title("4. DIAGNOSTICO Y PLAN")
                pdf.add_field("DX", pac['dx']); pdf.add_field("PLAN", pac['plan'])
                st.download_button("📥 Descargar HC", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]: # EVOLUCIÓN
            nueva = st.text_area("Nota Nueva:")
            if st.button("💾 Guardar Nota"):
                if nueva:
                    pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            if pac["notas_evolucion"] and st.button("📄 PDF Notas Evolución"):
                pdf_e = PEDIATRIC_PDF()
                pdf_e.add_page()
                pdf_e.section_title(f"NOTAS DE EVOLUCION: {pac['nombre']}")
                for n in pac["notas_evolucion"]:
                    pdf_e.add_field(n['f'], n['t'])
                st.download_button("📥 Descargar Notas", pdf_e.output(dest='S').encode('latin-1'), f"Evolucion_{pac['nombre']}.pdf")
            for n in pac["notas_evolucion"]: st.info(f"📅 {n['f']}\n{n['t']}")
