import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import json
import os

# --- 1. MOTOR DE PERSISTENCIA (JSON) ---
def cargar_db():
    if os.path.exists("db_pediatrica.json"):
        with open("db_pediatrica.json", "r") as f:
            return json.load(f)
    return {"usuarios": {"admin": "medico2026"}, "pacientes": {}}

def guardar_db():
    datos = {
        "usuarios": st.session_state["db_usuarios"],
        "pacientes": st.session_state["lista_pacientes_global"]
    }
    with open("db_pediatrica.json", "w") as f:
        json.dump(datos, f, default=str)
    st.sidebar.success("✅ ¡Base de datos actualizada!")

# Inicialización de la base de datos
if "db_usuarios" not in st.session_state:
    db = cargar_db()
    st.session_state["db_usuarios"] = db["usuarios"]
    st.session_state["lista_pacientes_global"] = db["pacientes"]

# --- 2. MOTOR DE PDF PROFESIONAL ---
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
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 9)
        self.write(6, f"{str(value)}\n")

# --- 3. GESTIÓN DE ACCESO ---
def login_registro():
    if "password_correct" not in st.session_state:
        st.title("🏥 Sistema Médico Pediátrico")
        choice = st.radio("Acceso", ["Iniciar Sesión", "Registrar Nuevo Médico"], horizontal=True)
        
        if choice == "Iniciar Sesión":
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
                    st.session_state["password_correct"] = True
                    st.session_state["user_actual"] = u
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas")
        else:
            nu = st.text_input("Definir Usuario Nuevo")
            np = st.text_input("Definir Contraseña", type="password")
            if st.button("Crear Cuenta Permanente"):
                if nu and np:
                    st.session_state["db_usuarios"][nu] = np
                    guardar_db() # Persiste el nuevo usuario inmediatamente
                    st.success(f"✨ Médico {nu} registrado. Ya puede iniciar sesión.")
        return False
    return True

# --- 4. APLICACIÓN PRINCIPAL ---
if login_registro():
    # Filtrar pacientes: Solo los que pertenecen al médico actual (Ecosistema Propio)
    usuario_id = st.session_state["user_actual"]
    mis_pacientes_ids = [pid for pid, pdata in st.session_state["lista_pacientes_global"].items() 
                         if pdata.get("doctor_owner") == usuario_id]

    with st.sidebar:
        st.write(f"🩺 Dr(a). **{usuario_id}**")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        
        st.divider()
        if st.button("💾 GUARDAR TODO EN BASE DE DATOS"):
            guardar_db()
        
        st.divider()
        if st.button("➕ NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes_global"][p_id] = {
                "doctor_owner": usuario_id, "nombre": "", "tipo_interrogatorio": "Directo",
                "informante": "", "parentesco": "", "telefono": "", "domicilio": "",
                "originario": "", "residente": "", "religion": "", "f_nac": date(2020,1,1),
                "sexo": "M", "edad": "", "fc": "", "fr": "", "sat": "", "temp": "",
                "ta": "", "glu": "", "peso": "", "talla": "", "ahf": "", "vacunas": "",
                "prenatales": "", "alimentacion": "", "natales": "", "apgar": "",
                "silverman": "", "desarrollo": "", "patologicos": "", "motivo": "",
                "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "",
                "as_urinario": "", "as_piel": "", "as_musculo": "", "exploracion": "",
                "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()

        if mis_pacientes_ids:
            st.session_state["paciente_seleccionado"] = st.selectbox("Mis Pacientes:", mis_pacientes_ids)
            if st.button("📊 Resumen de Turno"):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_title(f"Resumen de Guardia - Dr(a). {usuario_id}")
                for pid in mis_pacientes_ids:
                    p = st.session_state["lista_pacientes_global"][pid]
                    pdf_r.add_field("PACIENTE", f"{p['nombre']} ({p['edad']})")
                    pdf_r.add_field("DX", p['dx'])
                    pdf_r.ln(2)
                st.download_button("Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen.pdf")

    # Interfaz de Edición del Paciente Seleccionado
    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes_global"][st.session_state["paciente_seleccionado"]]
        st.header(f"Expediente: {pac['nombre'] if pac['nombre'] else 'Sin Nombre'}")
        
        t = st.tabs(["Filiación/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]: # FILIACIÓN + SIGNOS + SOMATOMETRÍA
            st.subheader("Ficha de Identificación")
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'] = c1.date_input("F. Nacimiento:", pac['f_nac'] if isinstance(pac['f_nac'], date) else date(2020,1,1))
            pac['edad'], pac['sexo'] = c2.text_input("Edad:", pac['edad']), c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
            c4, c5, c6 = st.columns(3)
            pac['tipo_interrogatorio'] = c4.selectbox("Interrogatorio:", ["Directo", "Indirecto", "Mixto"])
            pac['informante'], pac['parentesco'] = c5.text_input("Informante:", pac['informante']), c6.text_input("Parentesco:", pac['parentesco'])
            
            st.divider()
            st.subheader("Signos y Somatometría")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr']), s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", pac['ta']), s6.text_input("Glu:", pac['glu']), s7.text_input("Peso:", pac['peso']), s8.text_input("Talla:", pac['talla'])

        with t[1]: # ANTECEDENTES
            c1, c2, c3 = st.columns(3)
            pac['ahf'], pac['vacunas'] = c1.text_area("Heredo:", pac['ahf']), c1.text_area("Vacunas:", pac['vacunas'])
            pac['prenatales'], pac['alimentacion'] = c2.text_area("Pre:", pac['prenatales']), c2.text_area("Alimentación:", pac['alimentacion'])
            pac['natales'], pac['apgar'] = c3.text_area("Natales:", pac['natales']), c3.text_input("APGAR:", pac['apgar'])
            pac['patologicos'] = st.text_area("Patológicos:", pac['patologicos'])

        with t[2]: # SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:", pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:", pac['as_digestivo']), a2.text_area("Resp:", pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("Cardio:", pac['as_cardio']), a2.text_area("Neuro:", pac['as_neuro'])
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:", pac['as_musculo'])

        with t[3]: # EXPLORACIÓN
            pac['exploracion'] = st.text_area("Exploración Física:", pac['exploracion'], height=250)

        with t[4]: # DX/PLAN + PDF COMPLETO
            pac['dx'], pac['plan'] = st.text_area("Diagnóstico:", pac['dx']), st.text_area("Plan:", pac['plan'])
            if st.button("🖨️ GENERAR PDF HC"):
                pdf = PEDIATRIC_PDF()
                pdf.add_page()
                pdf.section_title("1. Filiación")
                pdf.add_field("Paciente", pac['nombre']); pdf.add_field("Interrogatorio", pac['tipo_interrogatorio'])
                pdf.section_title("2. Signos y Somatometría")
                pdf.add_field("Signos", f"FC:{pac['fc']} FR:{pac['fr']} T:{pac['temp']} TA:{pac['ta']}")
                pdf.add_field("Medidas", f"Peso:{pac['peso']} Talla:{pac['talla']} Glu:{pac['glu']}")
                pdf.section_title("3. Exploración Física")
                pdf.add_field("Hallazgos", pac['exploracion'])
                pdf.section_title("4. Diagnóstico y Plan")
                pdf.add_field("DX", pac['dx']); pdf.add_field("PLAN", pac['plan'])
                st.download_button("Descargar HC", pdf.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]: # EVOLUCIÓN
            nueva = st.text_area("Nota:")
            if st.button("💾 Guardar Nota"):
                pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                st.rerun()
            for n in pac["notas_evolucion"]: st.info(f"📅 {n['f']}\n{n['t']}")
