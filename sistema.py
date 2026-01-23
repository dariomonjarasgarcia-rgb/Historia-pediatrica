import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    if "password_correct" not in st.session_state:
        st.title("🏥 Sistema de Expedientes Pediátricos de Alta Especialidad")
        menu = ["Iniciar Sesión", "Registrarse"]
        choice = st.radio("Acceso al Sistema", menu, horizontal=True)
        if choice == "Iniciar Sesión":
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][user] == pwd:
                    st.session_state["password_correct"] = True
                    st.session_state["user_actual"] = user
                    if "lista_pacientes" not in st.session_state:
                        st.session_state["lista_pacientes"] = {}
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        else:
            new_user = st.text_input("Nuevo Usuario")
            new_pwd = st.text_input("Nueva Contraseña", type="password")
            if st.button("Crear Cuenta"):
                if new_user and new_pwd:
                    st.session_state["db_usuarios"][new_user] = new_pwd
                    st.success("✅ Cuenta creada.")
        return False
    return True

if login_registro():
    st.set_page_config(page_title="Expediente Pediátrico Avanzado", layout="wide")

    with st.sidebar:
        st.write(f"👨‍⚕️ Médico: **{st.session_state['user_actual']}**")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        if st.button("➕ AGREGAR NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "sexo": "M",
                "peso": "", "talla": "", "fc": "", "fr": "", "sat": "", "glu": "", "ta": "", "temp": "",
                "ahf": "", "prenatales": "", "natales": "", "neonatales": "",
                "apgar": "", "silverman": "", "vacunas": "", "alimentacion": "",
                "desarrollo": "", "patologicos": "", "motivo": "", "exploracion": "",
                "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "", "as_urinario": "", "as_musculo": "", "as_piel": "",
                "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()
        lista = list(st.session_state["lista_pacientes"].keys())
        if lista:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista)

    if st.session_state.get("paciente_seleccionado"):
        p = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        tabs = st.tabs(["👤 ID y Signos", "📋 Antecedentes", "🩺 Aparatos y Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with tabs[0]: # ID Y SIGNOS VITALES
            st.subheader("Ficha de Identificación")
            p['nombre'] = st.text_input("Nombre Completo:", value=p['nombre'])
            c1, c2 = st.columns(2)
            p['f_nac'] = c1.date_input("F. Nacimiento:", value=p['f_nac'])
            p['sexo'] = c2.selectbox("Sexo:", ["M", "F"], index=0 if p['sexo']=="M" else 1)
            st.divider()
            st.subheader("🩺 Signos Vitales")
            s1, s2, s3, s4 = st.columns(4)
            p['fc'], p['fr'], p['sat'], p['temp'] = s1.text_input("FC:", value=p['fc']), s2.text_input("FR:", value=p['fr']), s3.text_input("SatO2:", value=p['sat']), s4.text_input("Temp:", value=p['temp'])
            s5, s6, s7, s8 = st.columns(4)
            p['ta'], p['glu'], p['peso'], p['talla'] = s5.text_input("TA:", value=p['ta']), s6.text_input("Glu:", value=p['glu']), s7.text_input("Peso:", value=p['peso']), s8.text_input("Talla:", value=p['talla'])

        with tabs[1]: # ANTECEDENTES
            st.subheader("Historia Clínica: Antecedentes")
            col1, col2, col3 = st.columns(3)
            with col1:
                p['ahf'] = st.text_area("Heredo-Familiares:", value=p['ahf'])
                p['vacunas'] = st.text_area("Inmunizaciones/Tamiz:", value=p['vacunas'])
            with col2:
                p['prenatales'] = st.text_area("Prenatales:", value=p['prenatales'])
                p['alimentacion'] = st.text_area("Alimentación:", value=p['alimentacion'])
            with col3:
                p['natales'] = st.text_area("Natales:", value=p['natales'])
                p['apgar'] = st.text_input("APGAR:", value=p['apgar'])
                p['silverman'] = st.text_input("Silverman:", value=p['silverman'])
                p['desarrollo'] = st.text_area("Desarrollo:", value=p['desarrollo'])
            p['patologicos'] = st.text_area("Personales Patológicos:", value=p['patologicos'])

        with tabs[2]: # APARATOS Y SISTEMAS
            st.subheader("Interrogatorio por Sistemas")
            p['motivo'] = st.text_area("Padecimiento Actual:", value=p['motivo'])
            a1, a2 = st.columns(2)
            p['as_digestivo'], p['as_resp'] = a1.text_area("Digestivo:", value=p['as_digestivo']), a2.text_area("Respiratorio:", value=p['as_resp'])
            a3, a4 = st.columns(2)
            p['as_cardio'], p['as_neuro'] = a3.text_area("Cardio:", value=p['as_cardio']), a4.text_area("Neuro:", value=p['as_neuro'])
            a5, a6 = st.columns(2)
            p['as_urinario'], p['as_piel'] = a5.text_area("Urinario:", value=p['as_urinario']), a6.text_area("Piel:", value=p['as_piel'])
            p['as_musculo'] = st.text_area("Músculo-Esquelético:", value=p['as_musculo'])

        with tabs[3]: # EXPLORACIÓN
            p['exploracion'] = st.text_area("Exploración Física:", value=p['exploracion'], height=200)

        with tabs[4]: # DIAGNÓSTICO Y PLAN
            p['dx'] = st.text_area("Impresión Diagnóstica:", value=p['dx'])
            p['plan'] = st.text_area("Plan Terapéutico:", value=p['plan'])
            st.divider()
            
            if st.button("📝 PREPARAR PDF HISTORIA CLÍNICA"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "HISTORIA CLINICA PEDIATRICA", ln=True, align='C')
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Paciente: {p['nombre']} | Fecha: {date.today()}", ln=True)
                pdf.set_font("Arial", size=10)
                pdf.ln(5)
                # SECCIÓN SIGNOS
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(0, 8, "SIGNOS VITALES Y SOMATOMETRIA", ln=True, fill=True)
                pdf.multi_cell(0, 6, f"Peso: {p['peso']}kg | Talla: {p['talla']}cm | FC: {p['fc']} | FR: {p['fr']} | Sat: {p['sat']} | Temp: {p['temp']} | TA: {p['ta']} | Glu: {p['glu']}")
                # ANTECEDENTES
                pdf.ln(3)
                pdf.cell(0, 8, "ANTECEDENTES", ln=True, fill=True)
                pdf.multi_cell(0, 6, f"AHF: {p['ahf']}\nVacunas: {p['vacunas']}\nPrenatales: {p['prenatales']}\nNatales: {p['natales']} (APGAR: {p['apgar']} Silverman: {p['silverman']})\nAlimentacion: {p['alimentacion']}\nDesarrollo: {p['desarrollo']}\nPatologicos: {p['patologicos']}")
                # INTERROGATORIO
                pdf.ln(3)
                pdf.cell(0, 8, "INTERROGATORIO POR SISTEMAS", ln=True, fill=True)
                pdf.multi_cell(0, 6, f"Padecimiento Actual: {p['motivo']}\nDigestivo: {p['as_digestivo']}\nRespiratorio: {p['as_resp']}\nCardio: {p['as_cardio']}\nNeuro: {p['as_neuro']}\nUrinario: {p['as_urinario']}\nPiel: {p['as_piel']}\nMusculo: {p['as_musculo']}")
                # EXPLORACIÓN Y PLAN
                pdf.ln(3)
                pdf.cell(0, 8, "EXPLORACION, DX Y PLAN", ln=True, fill=True)
                pdf.multi_cell(0, 6, f"Exploracion: {p['exploracion']}\n\nDIAGNOSTICO: {p['dx']}\n\nPLAN: {p['plan']}")
                
                hc_bytes = pdf.output(dest='S').encode('latin-1')
                st.download_button(label="📥 DESCARGAR HISTORIA CLÍNICA COMPLETA", data=hc_bytes, file_name=f"HC_{p['nombre']}.pdf", mime="application/pdf")

        with tabs[5]: # EVOLUCIÓN
            nueva = st.text_area("Nueva Nota:")
            if st.button("Guardar Nota en Sistema"):
                if nueva:
                    p["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            st.divider()
            if p['notas_evolucion']:
                if st.button("📄 PREPARAR PDF EVOLUCIÓN"):
                    pdf_ev = FPDF()
                    pdf_ev.add_page()
                    pdf_ev.set_font("Arial", 'B', 14)
                    pdf_ev.cell(0, 10, f"NOTAS DE EVOLUCION: {p['nombre']}", ln=True, align='C')
                    pdf_ev.set_font("Arial", size=10)
                    for n in p["notas_evolucion"]:
                        pdf_ev.cell(0, 8, f"Fecha: {n['f']}", ln=True, fill=True)
                        pdf_ev.multi_cell(0, 6, f"{n['t']}\n")
                    ev_bytes = pdf_ev.output(dest='S').encode('latin-1')
                    st.download_button(label="📥 DESCARGAR TODAS LAS NOTAS", data=ev_bytes, file_name=f"Evolucion_{p['nombre']}.pdf", mime="application/pdf")
            for n in p["notas_evolucion"]:
                st.info(f"📅 {n['f']}\n{n['t']}")




