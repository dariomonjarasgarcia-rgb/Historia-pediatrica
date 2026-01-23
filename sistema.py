import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. CONFIGURACIÓN ESTÉTICA (CSS) ---
def apply_custom_design():
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px; background-color: #ffffff; padding: 10px; border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        }
        .stTabs [aria-selected="true"] {
            background-color: #007bff !important; color: white !important;
        }
        /* Estilo para los contenedores de inputs */
        div[data-testid="stVerticalBlock"] > div:has(div.stTextArea), 
        div[data-testid="stVerticalBlock"] > div:has(div.stTextInput) {
            background-color: #ffffff; padding: 15px; border-radius: 12px;
            border: 1px solid #e9ecef; margin-bottom: 5px;
        }
        .stButton>button {
            width: 100%; border-radius: 10px; height: 3em;
            background-color: #007bff; color: white; font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

def login_registro():
    apply_custom_design()
    if "password_correct" not in st.session_state:
        st.title("🏥 Expediente Pediátrico Pro")
        col_log1, col_log2, col_log3 = st.columns([1,2,1])
        with col_log2:
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
            else:
                nu = st.text_input("Nuevo Usuario")
                np = st.text_input("Nueva Contraseña", type="password")
                if st.button("✅ Crear Cuenta"):
                    st.session_state["db_usuarios"][nu] = np
                    st.success("Cuenta creada.")
        return False
    return True

if login_registro():
    st.set_page_config(page_title="Gestión Pediátrica Avanzada", layout="wide")
    apply_custom_design()

    # --- 3. BARRA LATERAL ---
    with st.sidebar:
        st.write(f"🩺 Dr(a). **{st.session_state['user_actual']}**")
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
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista_p)

        st.divider()
        # --- REGRESO DEL BOTÓN RESUMEN DE TURNO ---
        if st.session_state["lista_pacientes"]:
            st.subheader("Reporte de Turno")
            pdf_res = FPDF()
            pdf_res.add_page()
            pdf_res.set_font("Arial", 'B', 16)
            pdf_res.cell(0, 10, f"RESUMEN DE GUARDIA - {date.today()}", ln=True, align='C')
            pdf_res.set_font("Arial", size=10)
            for pid, pdata in st.session_state["lista_pacientes"].items():
                pdf_res.ln(5)
                pdf_res.cell(0, 8, f"PACIENTE: {pdata['nombre']} ({pdata['edad']})", ln=True, fill=True)
                pdf_res.multi_cell(0, 6, f"DX: {pdata['dx']}\nPLAN: {pdata['plan']}\n" + ("-"*30))
            
            res_bytes = pdf_res.output(dest='S').encode('latin-1')
            st.download_button(label="📊 DESCARGAR RESUMEN DE TURNO", data=res_bytes, file_name=f"Resumen_Turno_{date.today()}.pdf", mime="application/pdf")

    # --- 4. CUERPO MÉDICO ---
    if st.session_state.get("paciente_seleccionado"):
        p = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.markdown(f"# 🧒 {p['nombre'] if p['nombre'] else 'Nuevo Paciente'}")
        
        tabs = st.tabs(["👤 ID y Signos", "📋 Antecedentes", "🩺 Sistemas", "🔍 Exploración", "📝 DX/Plan", "📈 Evolución"])

        with tabs[0]: # ID Y SIGNOS (CON EDAD AÑADIDA)
            st.markdown("### 📝 Ficha de Identificación")
            p['nombre'] = st.text_input("Nombre Completo:", value=p['nombre'])
            c1, c2, c3 = st.columns(3)
            p['f_nac'] = c1.date_input("Fecha de Nacimiento:", value=p['f_nac'])
            p['edad'] = c2.text_input("Edad (ej. 5 años 2 meses):", value=p['edad'])
            p['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if p['sexo']=="M" else 1)
            
            st.markdown("### 🌡️ Signos Vitales")
            s1, s2, s3, s4 = st.columns(4)
            p['fc'], p['fr'], p['sat'], p['temp'] = s1.text_input("FC:", value=p['fc']), s2.text_input("FR:", value=p['fr']), s3.text_input("SatO2:", value=p['sat']), s4.text_input("Temp:", value=p['temp'])
            s5, s6, s7, s8 = st.columns(4)
            p['ta'], p['glu'], p['peso'], p['talla'] = s5.text_input("TA:", value=p['ta']), s6.text_input("Glu:", value=p['glu']), s7.text_input("Peso:", value=p['peso']), s8.text_input("Talla:", value=p['talla'])

        with tabs[1]: # ANTECEDENTES HORIZONTALES
            st.markdown("### 📋 Antecedentes")
            col1, col2, col3 = st.columns(3)
            with col1:
                p['ahf'] = st.text_area("Heredo-Familiares:", value=p['ahf'])
                p['vacunas'] = st.text_area("Vacunas/Tamiz:", value=p['vacunas'])
            with col2:
                p['prenatales'] = st.text_area("Prenatales:", value=p['prenatales'])
                p['alimentacion'] = st.text_area("Alimentación:", value=p['alimentacion'])
            with col3:
                p['natales'] = st.text_area("Natales (Parto):", value=p['natales'])
                c_n1, c_n2 = st.columns(2)
                p['apgar'], p['silverman'] = c_n1.text_input("APGAR:", value=p['apgar']), c_n2.text_input("Silverman:", value=p['silverman'])
                p['desarrollo'] = st.text_area("Desarrollo:", value=p['desarrollo'])
            p['patologicos'] = st.text_area("Patológicos:", value=p['patologicos'])

        with tabs[2]: # SISTEMAS
            st.markdown("### 🩺 Aparatos y Sistemas")
            p['motivo'] = st.text_area("Padecimiento Actual:", value=p['motivo'])
            a1, a2 = st.columns(2)
            p['as_digestivo'], p['as_resp'] = a1.text_area("Digestivo:", value=p['as_digestivo']), a2.text_area("Respiratorio:", value=p['as_resp'])
            a3, a4 = st.columns(2)
            p['as_cardio'], p['as_neuro'] = a3.text_area("Cardio:", value=p['as_cardio']), a4.text_area("Neuro:", value=p['as_neuro'])
            a5, a6 = st.columns(2)
            p['as_urinario'], p['as_piel'] = a5.text_area("Urinario:", value=p['as_urinario']), a6.text_area("Piel:", value=p['as_piel'])
            p['as_musculo'] = st.text_area("Músculo-Esquelético:", value=p['as_musculo'])

        with tabs[3]: # EXPLORACIÓN
            st.markdown("### 🔍 Exploración Física")
            p['exploracion'] = st.text_area("Hallazgos:", value=p['exploracion'], height=250)

        with tabs[4]: # DX/PLAN Y PDF
            st.markdown("### 📝 Conclusión")
            p['dx'] = st.text_area("Diagnóstico:", value=p['dx'])
            p['plan'] = st.text_area("Plan:", value=p['plan'])
            st.divider()
            if st.button("📄 PREPARAR PDF HISTORIA CLÍNICA"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "HISTORIA CLINICA PEDIATRICA", ln=True, align='C')
                pdf.set_font("Arial", size=10)
                pdf.ln(5)
                pdf.multi_cell(0, 6, f"Paciente: {p['nombre']} | Edad: {p['edad']}\nDX: {p['dx']}\nPLAN: {p['plan']}")
                hc_b = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 DESCARGAR HISTORIA", data=hc_b, file_name=f"HC_{p['nombre']}.pdf")

        with tabs[5]: # EVOLUCIÓN
            st.markdown("### 📈 Notas de Evolución")
            nueva = st.text_area("Nota actual:")
            if st.button("💾 Guardar Nota"):
                if nueva:
                    p["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            if p['notas_evolucion']:
                pdf_e = FPDF()
                pdf_e.add_page()
                pdf_e.set_font("Arial", 'B', 14)
                pdf_e.cell(0, 10, f"NOTAS: {p['nombre']}", ln=True)
                for n in p["notas_evolucion"]:
                    pdf_e.multi_cell(0, 6, f"{n['f']}: {n['t']}\n")
                ev_b = pdf_e.output(dest='S').encode('latin-1')
                st.download_button("📥 DESCARGAR NOTAS", data=ev_b, file_name=f"Evolucion_{p['nombre']}.pdf")
            for n in p["notas_evolucion"]: st.info(f"📅 {n['f']}\n{n['t']}")
