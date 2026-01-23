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

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.header(f"🧑‍⚕️ {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")

        t = st.tabs(["Filiación/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]: # FILIACIÓN Y SIGNOS ACTUALIZADO
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
            pac['telefono'], pac['religion'] = c7.text_input("Teléfono:"), c8.text_input("Religión:")
            pac['domicilio'] = st.text_input("Domicilio:")
            pac['originario'], pac['residente'] = st.columns(2)[0].text_input("Originario:"), st.columns(2)[1].text_input("Residente:")

            st.subheader("Signos Vitales y Somatometría")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:"), s2.text_input("FR:"), s3.text_input("SatO2:"), s4.text_input("Temp:")
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:"), s6.text_input("Glu:"), s7.text_input("Peso (kg):"), s8.text_input("Talla (cm):")

        with t[1]: # ANTECEDENTES
            c1, c2, c3 = st.columns(3)
            pac['ahf'], pac['vacunas'] = c1.text_area("Heredofamiliares:"), c1.text_area("Vacunas:")
            pac['prenatales'], pac['alimentacion'] = c2.text_area("Prenatales:"), c2.text_area("Alimentación:")
            pac['natales'] = c3.text_area("Natales:")
            pac['apgar'], pac['silverman'] = c3.text_input("APGAR:"), c3.text_input("Silverman:")
            pac['desarrollo'], pac['patologicos'] = c3.text_area("Desarrollo:"), st.text_area("Patológicos:")

        with t[2]: # SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:")
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:"), a2.text_area("Respiratorio:")
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("Cardio:"), a2.text_area("Neuro:")
            pac['as_urinario'], pac['as_piel'] = a1.text_area("Urinario:"), a2.text_area("Piel:")
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:")

        with t[3]: # EXPLORACIÓN
            pac['exploracion'] = st.text_area("Exploración Física:", height=300)

        with t[4]: # DX Y PLAN
            pac['dx'], pac['plan'] = st.text_area("Diagnóstico:", height=150), st.text_area("Plan:", height=200)
            if st.button("🖨️ GENERAR PDF HISTORIA CLINICA"):
                pdf = PEDIATRIC_PDF()
                pdf.add_page()
                pdf.section_title("1. Filiación e Interrogatorio")
                pdf.add_field("Paciente", pac['nombre']); pdf.add_field("Edad/Sexo", f"{pac['edad']} / {pac['sexo']}")
                pdf.add_field("Interrogatorio", f"{pac['tipo_interrogatorio']} (Informante: {pac['informante']} - {pac['parentesco']})")
                pdf.add_field("Domicilio", pac['domicilio'])
                pdf.section_title("2. Somatometría y Signos")
                pdf.add_field("Signos", f"FC:{pac['fc']} FR:{pac['fr']} Sat:{pac['sat']} T:{pac['temp']} TA:{pac['ta']}")
                pdf.add_field("Somatometría", f"Peso:{pac['peso']}kg Talla:{pac['talla']}cm Glu:{pac['glu']}")
                pdf.section_title("3. Exploración Física")
                pdf.add_field("Detalle", pac['exploracion'])
                pdf.section_title("4. Diagnóstico y Plan")
                pdf.add_field("DX", pac['dx']); pdf.add_field("PLAN", pac['plan'])
                st.download_button("Descargar HC", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]: # EVOLUCIÓN CON ESTILO
            st.subheader("Notas de Evolución")
            nueva = st.text_area("Escribir nota:")
            if st.button("💾 Guardar Nota"):
                if nueva:
                    pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            if pac["notas_evolucion"] and st.button("📄 GENERAR PDF DE NOTAS"):
                pdf_e = PEDIATRIC_PDF()
                pdf_e.add_page()
                pdf_e.section_title(f"HISTORIAL DE EVOLUCION: {pac['nombre']}")
                for n in pac["notas_evolucion"]:
                    pdf_e.set_font('Arial', 'B', 10); pdf_e.cell(0, 7, f"Fecha: {n['f']}", 0, 1)
                    pdf_e.set_font('Arial', '', 10); pdf_e.multi_cell(0, 6, n['t'])
                    pdf_e.ln(4); pdf_e.line(10, pdf_e.get_y(), 200, pdf_e.get_y())
                st.download_button("Descargar Notas", pdf_e.output(dest='S').encode('latin-1'), f"Notas_{pac['nombre']}.pdf")
            for n in pac["notas_evolucion"]: st.info(f"📅 {n['f']}\n{n['t']}")
