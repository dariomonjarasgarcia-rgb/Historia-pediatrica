import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io
import json
import os
# IMPORTA LAS FUNCIONES DE TU ARCHIVO interface_premium.py
from interface_premium import cargar_estilo_hospital

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Hospitalaria Pediátrica", layout="wide", page_icon="🏥")
cargar_estilo_hospital()

# --- PERSISTENCIA DE USUARIOS (Base de Datos Simple) ---
def cargar_usuarios():
    if os.path.exists("usuarios.json"):
        with open("usuarios.json", "r") as f:
            return json.load(f)
    return {"admin": "medico2026"}

def guardar_usuario(usuario, password):
    usuarios = cargar_usuarios()
    usuarios[usuario] = password
    with open("usuarios.json", "w") as f:
        json.dump(usuarios, f)

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

# --- LÓGICA DE ACCESO ---
def login_registro():
    if "db_usuarios" not in st.session_state:
        st.session_state["db_usuarios"] = cargar_usuarios()

    if "password_correct" not in st.session_state:
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
                        else: st.error("Usuario o contraseña incorrectos")
                else:
                    nu = st.text_input("Nuevo Usuario")
                    np = st.text_input("Contraseña", type="password")
                    if st.button("Crear Cuenta", use_container_width=True):
                        if nu in st.session_state["db_usuarios"]:
                            st.warning("El usuario ya existe")
                        else:
                            guardar_usuario(nu, np)
                            st.session_state["db_usuarios"] = cargar_usuarios()
                            st.success("✅ ¡Registro exitoso! Ya puedes iniciar sesión.")
        return False
    return True

# --- INICIO DE LA APLICACIÓN ---
if login_registro():
    # Sidebar corregido (sin duplicados)
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

    # Cuerpo Principal
    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.title(f"👤 {pac['nombre'] if pac['nombre'] else 'Paciente Nuevo'}")
        
        t = st.tabs(["📋 Filiación", "🧬 Antecedentes", "🫁 Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with t[0]: # FILIACIÓN EN TARJETA
            with st.container(border=True):
                st.subheader("Datos de Filiación")
                pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
                c1, c2, c3 = st.columns(3)
                pac['f_nac'] = c1.date_input("Nacimiento:", pac['f_nac'])
                pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
                pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
                
                # ... Aquí sigue el resto de tus campos organizados en columnas ...
                st.info("Formulario optimizado para visualización clínica.")
