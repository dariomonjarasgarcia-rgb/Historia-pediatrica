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

# --- MOTORES PDF ---
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
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, '__________________________________________', 0, 1, 'C')
        self.cell(0, 5, f'Firma del Medico', 0, 0, 'C')

# --- SISTEMA DE LOGIN ---
def login_registro():
    if "db_usuarios" not in st.session_state: st.session_state["db_usuarios"] = cargar_usuarios()
    if "password_correct" not in st.session_state:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            with st.container(border=True):
                st.title("📂 Acceso Clinico")
                choice = st.radio("Accion", ["Iniciar Sesion", "Registrarse"], horizontal=True)
                u = st.text_input("Usuario")
                p = st.text_input("Contraseña", type="password")
                if choice == "Iniciar Sesion":
                    if st.button("Ingresar", use_container_width=True, type="primary"):
                        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                            st.session_state["password_correct"] = True
                            st.session_state["user_actual"] = u
                            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                            st.rerun()
                        else: st.error("Credenciales incorrectas")
                else:
                    if st.button("Crear Cuenta", use_container_width=True):
                        guardar_usuario(u, p)
                        st.success("Usuario registrado")
        return False
    return True

# --- LOGICA PRINCIPAL ---
if login_registro():
    with st.sidebar:
        st.header(f"🩺 Dr. {st.session_state.get('user_actual', 'Medico')}")
        if st.button("Cerrar Sesion"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        if st.button("➕ NUEVO PACIENTE", type="primary"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "edad": "", "sexo": "M",
                "fc": "", "fr": "", "sat": "", "temp": "",
                "ahf": "", "prenatales": "", "natales": "", "vacunas": "",
                "as_digestivo": "", "as_cardio": "", "as_urinario": "", "as_resp": "",
                "as_neuro": "", "as_piel": "", "as_musculo": "",
                "motivo": "", "exploracion": "", "dx": "", "plan": "",
                "notas_evolucion": [], "receta_texto": ""
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()
        
        opciones = list(st.session_state.get("lista_pacientes", {}).keys())
        if opciones:
            st.session_state["paciente_seleccionado"] = st.selectbox("Seleccionar Expediente", opciones)

    if "paciente_seleccionado" in st.session_state:
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.title(f"👤 {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")

        t = st.tabs(["Filiacion", "Antecedentes", "Sistemas", "Exploracion", "DX/Plan", "Receta", "Evolucion"])

        with t[0]: # FILIACION
            with st.container(border=True):
                pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
                c1, c2, c3 = st.columns(3)
                pac['f_nac'] = c1.date_input("Fecha Nacimiento:", pac['f_nac'])
                pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
                pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
            with st.container(border=True):
                st.subheader("Signos Vitales")
                s1, s2, s3, s4 = st.columns(4)
                pac['fc'] = s1.text_input("FC:", value=pac['fc'])
                pac['fr'] = s2.text_input("FR:", value=pac['fr'])
                pac['sat'] = s3.text_input("SatO2:", value=pac['sat'])
                pac['temp'] = s4.text_input("Temp:", value=pac['temp'])

        with t[1]: # ANTECEDENTES
            col1, col2 = st.columns(2)
            pac['ahf'] = col1.text_area("Heredofamiliares:", value=pac['ahf'])
            pac['prenatales'] = col2.text_area("Prenatales:", value=pac['prenatales'])
            pac['natales'] = col1.text_area("Natales:", value=pac['natales'])
            pac['vacunas'] = col2.text_area("Vacunas:", value=pac['vacunas'])

        with t[2]: # SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:", value=pac['motivo'])
            col_a, col_b = st.columns(2)
            pac['as_digestivo'] = col_a.text_area("Digestivo:", value=pac['as_digestivo'])
            pac['as_cardio'] = col_b.text_area("Cardiovascular:", value=pac['as_
