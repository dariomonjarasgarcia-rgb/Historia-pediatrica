import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. CONFIGURACIÓN DE INTERFAZ (FORZADO MODO CLARO) ---
st.set_page_config(page_title="Expediente Pediátrico Pro", layout="wide")

def apply_ui_fix():
    st.markdown("""
        <style>
        /* Forzar fondo blanco y texto negro en toda la app */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: white !important;
            color: black !important;
        }
        /* Forzar que todos los labels, titulos y textos sean negros legibles */
        h1, h2, h3, h4, p, label, .stMarkdown, .stSelectbox p, div[data-baseweb="tab"] p {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        /* Cajas de entrada con fondo gris muy claro y borde azul para que se vean */
        .stTextInput input, .stTextArea textarea, .stDateInput input {
            background-color: #F8F9FB !important;
            color: black !important;
            border: 2px solid #007bff !important;
        }
        /* Pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] { background-color: #FFFFFF !important; border-bottom: 2px solid #007bff; }
        .stTabs [data-baseweb="tab"] { background-color: #E9ECEF !important; border-radius: 5px 5px 0 0; margin-right: 5px; }
        .stTabs [aria-selected="true"] { background-color: #007bff !important; }
        .stTabs [aria-selected="true"] p { color: white !important; }

        /* Botones principales */
        .stButton>button {
            background-color: #007bff !important;
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: bold;
            padding: 10px 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE PDF PROFESIONAL ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 102, 204) # Azul fuerte
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'HISTORIA CLINICA PEDIATRICA', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(20)

    def section_title(self, txt):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, f" {txt}", 0, 1, 'L', fill=True)
        self.ln(3)

    def add_field(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(60, 60, 60)
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.write(6, f"{str(value)}\n")

# --- 3. GESTIÓN DE DATOS ---
if "db_usuarios" not in st.session_state: st.session_state["db_usuarios"] = {"admin": "medico2026"}

if "password_correct" not in st.session_state:
    apply_ui_fix()
    st.title("🔐 Acceso Restringido")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
            st.session_state["password_correct"] = True
            st.session_state["user_actual"] = u
            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
            st.rerun()
else:
    apply_ui_fix()
    with st.sidebar:
        st.write(f"🩺 Dr(a). {st.session_state['user_actual']}")
        if st.button("➕ NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
                "peso": "", "talla": "", "fc": "", "fr": "", "sat": "", "glu": "", "ta": "", "temp": "",
                "ahf": "", "prenatales": "", "natales": "", "apgar": "", "silverman": "",
                "vacunas": "", "alimentacion": "", "desarrollo": "", "patologicos": "", 
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
            # RESUMEN DE TURNO (SIDEBAR)
            if st.button("📊 Preparar Resumen de Turno"):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_title("Resumen de Guardia Actual")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.add_field("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                    pdf_r.add_field("DIAGNOSTICO", pdata['dx'])
                    pdf_r.ln(2)
                st.download_button("📥 Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen_Guardia.pdf")

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.markdown(f"## 🧒 Paciente: {pac['nombre']}")

        t = st.tabs(["ID/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]: # ID Y SIGNOS
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'], pac['edad'], pac['sexo'] = c1.date_input("F. Nacimiento:", pac['f_nac']), c2.text_input("Edad:", pac['edad']), c3.selectbox("Sexo:", ["M", "F"])
            st.markdown("---")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr']), s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", pac['ta']), s6.text_input("Glu:", pac['glu']), s7.text_input("Peso:", pac['peso']), s8.text_input("Talla:", pac['talla'])

        with t[1]: # ANTECEDENTES (3 COLUMNAS)
            c1, c2, c3 = st.columns(3)
            pac['ahf'] = c1.text_area("Heredo-Familiares:", pac['ahf'])
            pac['vacunas'] = c1.text_area("Inmunizaciones/Tamiz:", pac['vacunas'])
            pac['prenatales'] = c2.text_area("Prenatales:", pac['prenatales'])
            pac['alimentacion'] = c2.text_area("Alimentación:", pac['alimentacion'])
            pac['natales'] = c3.text_area("Natales (Parto):", pac['natales'])
            pac['apgar'], pac['silverman'] = c3.text_input("APGAR:", pac['apgar']), c3.text_input("Silverman:", pac['silverman'])
            pac['desarrollo'] = c3.text_area("Hitos Desarrollo:", pac['desarrollo'])
            pac['patologicos'] = st.text_area("Antecedentes Patológicos:", pac['patologicos'])

        with t[2]: # SISTEMAS
            pac['motivo'] = st.text_area("Padecimiento Actual:", pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:", pac['as_digestivo']), a2.text_area("Respiratorio:", pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("Cardiovascular:", pac['as_cardio']), a2.text_area("Neurológico:", pac['as_neuro'])
            pac['as_urinario'], pac['as_piel'] = a1.text_area("Urinario:", pac['as_urinario']), a2.text_area("Piel/Faneras:", pac['as_piel'])
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:", pac['as_musculo'])

        with t[3]: # EXPLORACIÓN
            pac['exploracion'] = st.text_area("Exploración Física Detallada:", pac['exploracion'], height=300)

        with t[4]: # DIAGNÓSTICO, PLAN Y BOTÓN PDF
            pac['dx'], pac['plan'] = st.text_area("Impresión Diagnóstica:", pac['dx']), st.text_area("Plan de Manejo:", pac['plan'])
            st.divider()
            if st.button("🖨️ Preparar PDF Historia Clínica Completa"):
                pdf = PEDIATRIC_PDF()
                pdf.add_page()
                pdf.section_title("Datos de Identificacion")
                pdf.add_field("Nombre", pac['nombre'])
                pdf.add_field("Edad", pac['edad'])
                pdf.add_field("Signos", f"FC:{pac['fc']} FR:{pac['fr']} Sat:{pac['sat']} Temp:{pac['temp']} TA:{pac['ta']} Peso:{pac['peso']} Talla:{pac['talla']} Glu:{pac['glu']}")
                pdf.section_title("Antecedentes")
                pdf.add_field("AHF", pac['ahf'])
                pdf.add_field("Vacunas", pac['vacunas'])
                pdf.add_field("Prenatales", pac['prenatales'])
                pdf.add_field("Natales", f"{pac['natales']} (APGAR:{pac['apgar']} SV:{pac['silverman']})")
                pdf_hc_out = pdf.output(dest='S').encode('latin-1')
                st.download_button("📥 Descargar Historia Clínica", pdf_hc_out, f"HC_{pac['nombre']}.pdf")

        with t[5]: # EVOLUCIÓN
            nueva = st.text_area("Nueva Nota:")
            if st.button("💾 Guardar Nota"):
                pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                st.rerun()
            if pac["notas_evolucion"] and st.button("📄 Generar PDF Notas Evolución"):
                pdf_e = PEDIATRIC_PDF()
                pdf_e.add_page()
                pdf_e.section_title(f"Historial de Notas: {pac['nombre']}")
                for n in pac["notas_evolucion"]:
                    pdf_e.add_field(n['f'], n['t'])
                    pdf_e.ln(2)
                st.download_button("📥 Descargar Evolución", pdf_e.output(dest='S').encode('latin-1'), f"Evolucion_{pac['nombre']}.pdf")
            for n in pac["notas_evolucion"]: st.info(f"{n['f']}: {n['t']}")
