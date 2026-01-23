import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO FORZADO ---
st.set_page_config(page_title="Expediente Pediátrico Pro", layout="wide")

def apply_custom_design():
    st.markdown("""
        <style>
        /* Forzar colores base para evitar conflicto con Modo Oscuro */
        .stApp {
            background-color: #f8f9fa !important;
            color: #1a1a1a !important;
        }
        
        /* Ajustar todos los textos de etiquetas (Labels) */
        label, .stMarkdown, p, h1, h2, h3 {
            color: #1a1a1a !important;
        }

        /* Estilo de las Pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #ffffff;
            padding: 10px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f1f3f5;
            border-radius: 8px;
            color: #495057 !important;
            padding: 8px 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #007bff !important;
            color: white !important;
        }

        /* Estilo de las cajas de entrada (Inputs) */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
            background-color: #ffffff !important;
            color: #1a1a1a !important;
            border: 1px solid #ced4da !important;
            border-radius: 8px !important;
        }

        /* Sidebar (Barra Lateral) */
        section[data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e9ecef;
        }
        section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
            color: #1a1a1a !important;
        }

        /* Botones */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            background-color: #007bff;
            color: white !important;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    apply_custom_design()
    if "password_correct" not in st.session_state:
        st.title("🏥 Sistema Médico Pediátrico")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            menu = ["Iniciar Sesión", "Registrarse"]
            choice = st.radio("Acceso", menu, horizontal=True)
            if choice == "Iniciar Sesión":
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.button("🚀 Ingresar"):
                    if user in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][user] == pwd:
                        st.session_state["password_correct"] = True
                        st.session_state["user_actual"] = user
                        if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
                        st.rerun()
                    else: st.error("❌ Error de acceso")
            else:
                nu = st.text_input("Nuevo Usuario")
                np = st.text_input("Nueva Contraseña", type="password")
                if st.button("✅ Crear Cuenta"):
                    st.session_state["db_usuarios"][nu] = np
                    st.success("Cuenta creada. Ya puede iniciar sesión.")
        return False
    return True

if login_registro():
    apply_custom_design()

    # --- 3. BARRA LATERAL ---
    with st.sidebar:
        st.markdown(f"### 👨‍⚕️ Dr(a). {st.session_state['user_actual']}")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        if st.button("➕ NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
                "peso": "", "talla": "", "fc": "", "fr": "", "sat": "", "glu": "", "ta": "", "temp": "",
                "ahf": "", "prenatales": "", "natales": "", "neonatales": "",
                "apgar": "", "silverman": "", "vacunas": "", "alimentacion": "",
                "desarrollo": "", "patologicos": "", "motivo": "", "exploracion": "",
                "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "", "as_urinario": "", "as_musculo": "", "as_piel": "",
                "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()
        
        lista_p = list(st.session_state["lista_pacientes"].keys())
        if lista_p:
            st.session_state["paciente_seleccionado"] = st.selectbox("Seleccionar Expediente:", lista_p)

        st.divider()
        if st.session_state["lista_pacientes"]:
            st.markdown("### 📊 Reporte de Turno")
            pdf_res = FPDF()
            pdf_res.add_page()
            pdf_res.set_font("Arial", 'B', 16)
            pdf_res.cell(0, 10, f"RESUMEN DE GUARDIA - {date.today()}", ln=True, align='C')
            pdf_res.set_font("Arial", size=10)
            for pid, pdata in st.session_state["lista_pacientes"].items():
                pdf_res.ln(5)
                pdf_res.cell(0, 8, f"PACIENTE: {pdata['nombre']} ({pdata['edad']})", ln=True)
                pdf_res.multi_cell(0, 6, f"DX: {pdata['dx']}\nPLAN: {pdata['plan']}\n" + ("-"*30))
            res_bytes = pdf_res.output(dest='S').encode('latin-1')
            st.download_button(label="📥 DESCARGAR RESUMEN TOTAL", data=res_bytes, file_name=f"Turno_{date.today()}.pdf", mime="application/pdf")

    # --- 4. CUERPO MÉDICO ---
    if st.session_state.get("paciente_seleccionado"):
        p = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.markdown(f"# 🧒 Paciente: {p['nombre']}")
        
        tabs = st.tabs(["👤 ID y Signos", "📋 Antecedentes", "🩺 Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with tabs[0]: 
            st.markdown("### 📝 Ficha de Identificación")
            p['nombre'] = st.text_input("Nombre Completo:", value=p['nombre'])
            c1, c2, c3 = st.columns(3)
            p['f_nac'] = c1.date_input("Fecha de Nacimiento:", value=p['f_nac'])
            p['edad'] = c2.text_input("Edad Actual:", value=p['edad'])
            p['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if p['sexo']=="M" else 1)
            
            st.markdown("### 🌡️ Signos Vitales")
            s1, s2, s3, s4 = st.columns(4)
            p['fc'], p['fr'], p['sat'], p['temp'] = s1.text_input("FC:", value=p['fc']), s2.text_input("FR:", value=p['fr']), s3.text_input("SatO2:", value=p['sat']), s4.text_input("Temp:", value=p['temp'])
            s5, s6, s7, s8 = st.columns(4)
            p['ta'], p['glu'], p['peso'], p['talla'] = s5.text_input("TA:", value=p['ta']), s6.text_input("Glu:", value=p['glu']), s7.text_input("Peso:", value=p['peso']), s8.text_input("Talla:", value=p['talla'])

        with tabs[1]: 
            st.markdown("### 📋 Antecedentes Detallados")
            col1, col2, col3 = st.columns(3)
            with col1:
                p['ahf'] = st.text_area("Heredo-Familiares:", value=p['ahf'])
                p['vacunas'] = st.text_area("Vacunas/Tamiz:", value=p['vacunas'])
            with col2:
                p['prenatales'] = st.text_area("Prenatales:", value=p['prenatales'])
                p['alimentacion'] = st.text_area("Alimentación:", value=p['alimentacion'])
            with col3:
                p['natales'] = st.text_area("Natales (Parto):", value=p['natales'])
                p['apgar'] = st.text_input("APGAR:", value=p['apgar'])
                p['silverman'] = st.text_input("Silverman:", value=p['silverman'])
                p['desarrollo'] = st.text_area("Hitos del Desarrollo:", value=p['desarrollo'])
            p['patologicos'] = st.text_area("Personales Patológicos (Alergias, Qx, etc):", value=p['patologicos'])

        with tabs[2]: 
            st.markdown("### 🩺 Interrogatorio por Sistemas")
            p['motivo'] = st.text_area("Padecimiento Actual:", value=p['motivo'])
            a1, a2 = st.columns(2)
            p['as_digestivo'], p['as_resp'] = a1.text_area("Digestivo:", value=p['as_digestivo']), a2.text_area("Respiratorio:", value=p['as_resp'])
            a3, a4 = st.columns(2)
            p['as_cardio'], p['as_neuro'] = a3.text_area("Cardio:", value=p['as_cardio']), a4.text_area("Neuro:", value=p['as_neuro'])
            a5, a6 = st.columns(2)
            p['as_urinario'], p['as_piel'] = a5.text_area("Urinario:", value=p['as_urinario']), a6.text_area("Piel:", value=p['as_piel'])
            p['as_musculo'] = st.text_area("Músculo-Esquelético:", value=p['as_musculo'])

        with tabs[3]: 
            st.markdown("### 🔍 Exploración Física")
            p['exploracion'] = st.text_area("Hallazgos Clínicos:", value=p['exploracion'], height=250)

        with tabs[4]: 
            st.markdown("### 📝 Diagnóstico y Plan")
            p['dx'] = st.text_area("Diagnóstico Final:", value=p['dx'])
            p['plan'] = st.text_area("Plan Terapéutico:", value=p['plan'])
            st.divider()
            pdf_hc = FPDF()
            pdf_hc.add_page()
            pdf_hc.set_font("Arial", 'B', 16)
            pdf_hc.cell(0, 10, f"HISTORIA CLINICA - {p['nombre']}", ln=True, align='C')
            pdf_hc.set_font("Arial", size=10)
            pdf_hc.ln(10)
            pdf_hc.multi_cell(0, 7, f"EDAD: {p['edad']}\nDX: {p['dx']}\nPLAN: {p['plan']}")
            hc_b = pdf_hc.output(dest='S').encode('latin-1')
            st.download_button("📥 DESCARGAR HISTORIA CLÍNICA PDF", data=hc_b, file_name=f"HC_{p['nombre']}.pdf")

        with tabs[5]: 
            st.markdown("### 📈 Evolución")
            nueva = st.text_area("Escribir nueva nota:")
            if st.button("💾 Guardar Nota"):
                if nueva:
                    p["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            for n in p["notas_evolucion"]:
                st.info(f"📅 {n['f']}\n{n['t']}")
