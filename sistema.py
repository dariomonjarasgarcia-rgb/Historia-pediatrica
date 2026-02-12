import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io
import json
import os
from interface_premium import cargar_estilo_hospital

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Hospitalaria Pediátrica", layout="wide", page_icon="🏥")
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

# --- MOTOR PDF ---
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

# --- LOGIN / REGISTRO ---
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

# --- APP ---
if login_registro():
    with st.sidebar:
        st.write(f"🩺 Dr(a). **{st.session_state['user_actual']}**")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            del st.session_state["password_correct"]; st.rerun()
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
            st.session_state["paciente_seleccionado"] = p_id; st.rerun()
        
        lista_p = list(st.session_state["lista_pacientes"].keys())
        if lista_p:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista_p)
            if st.button("📊 Generar Resumen", use_container_width=True):
                pdf_r = PEDIATRIC_PDF(); pdf_r.add_page(); pdf_r.section_title("Resumen Guardia")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.add_field("PACIENTE", f"{pdata['nombre']}"); pdf_r.ln(2)
                st.download_button("📥 Descargar", pdf_r.output(dest='S').encode('latin-1'), "Resumen.pdf")

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.header(f"🧑‍⚕️ {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")

        t = st.tabs(["📋 Filiación/Signos", "🧬 Antecedentes", "🫁 Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with t[0]: # FILIACIÓN
            with st.container(border=True):
                st.subheader("Datos de Filiación")
                pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
                c1, c2, c3 = st.columns(3)
                pac['f_nac'], pac['edad'], pac['sexo'] = c1.date_input("Nacimiento:", pac['f_nac']), c2.text_input("Edad:", value=pac['edad']), c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
                st.divider()
                c4, c5, c6 = st.columns(3)
                pac['tipo_interrogatorio'], pac['informante'], pac['parentesco'] = c4.selectbox("Interrogatorio:", ["Directo", "Indirecto", "Mixto"]), c5.text_input("Informante:"), c6.text_input("Relación:")
            with st.container(border=True):
                st.subheader("Signos Vitales")
                s1, s2, s3, s4 = st.columns(4)
                pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:"), s2.text_input("FR:"), s3.text_input("SatO2:"), s4.text_input("Temp:")

        with t[1]: # ANTECEDENTES
            with st.container(border=True):
                c1, c2, c3 = st.columns(3)
                pac['ahf'] = c1.text_area("Heredofamiliares:", value=pac['ahf'])
                pac['vacunas'] = c1.text_area("Vacunas:", value=pac['vacunas'])
                pac['prenatales'] = c2.text_area("Prenatales:", value=pac['prenatales'])
                pac['alimentacion'] = c2.text_area("Alimentación:", value=pac['alimentacion'])
                pac['natales'] = c3.text_area("Natales:", value=pac['natales'])
                pac['desarrollo'] = c3.text_area("Hitos Desarrollo:", value=pac['desarrollo'])

        with t[2]: # SISTEMAS
            with st.container(border=True):
                pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'])
                a1, a2 = st.columns(2)
                pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:"), a2.text_area("Respiratorio:")

        with t[3]: # EXPLORACIÓN
            with st.container(border=True):
                pac['exploracion'] = st.text_area("Exploración Física:", value=pac['exploracion'], height=300)

        with t[4]: # DX/PLAN
            with st.container(border=True):
                pac['dx'], pac['plan'] = st.text_area("Impresión Diagnóstica:", value=pac['dx']), st.text_area("Plan:", value=pac['plan'])
                if st.button("🖨️ GENERAR HISTORIA COMPLETA", type="primary", use_container_width=True):
                    pdf = PEDIATRIC_PDF(); pdf.add_page(); pdf.section_title("Historia Clínica")
                    pdf.add_field("Paciente", pac['nombre']); pdf.add_field("DX", pac['dx'])
                    st.download_button("📥 Descargar PDF", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf", use_container_width=True)

        with t[5]: # EVOLUCIÓN
            with st.container(border=True):
                st.subheader("Notas de Evolución")
                nueva = st.text_area("Escribir nota:")
                if st.button("💾 Guardar Nota", use_container_width=True, type="primary"):
                    if nueva:
                        pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                        st.rerun()
                for n in pac["notas_evolucion"]: st.info(f"📅 {n['f']}\n{n['t']}")
