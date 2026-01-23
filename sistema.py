import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. CONFIGURACIÓN DE PÁGINA Y COLORES INMEDIATOS ---
st.set_page_config(page_title="Expediente Pediátrico Pro", layout="wide")

def apply_ui_fix():
    st.markdown("""
        <style>
        /* Bloqueo de colores para evitar conflictos de modo oscuro */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: white !important;
            color: black !important;
        }
        /* Forzar visibilidad de textos */
        h1, h2, h3, h4, p, label, .stMarkdown, .stSelectbox p {
            color: #1a1a1a !important;
            font-weight: 500;
        }
        /* Cajas de texto con contraste */
        .stTextInput input, .stTextArea textarea {
            background-color: #f9f9f9 !important;
            color: black !important;
            border: 1px solid #007bff !important;
        }
        /* Pestañas */
        .stTabs [data-baseweb="tab-list"] { background-color: white !important; border-bottom: 2px solid #007bff; }
        .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE PDF PROFESIONAL (TODOS LOS DATOS) ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 86, 179)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'EXPEDIENTE CLINICO PEDIATRICO', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(15)

    def section_header(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 86, 179)
        self.cell(0, 7, f" {title.upper()}", 0, 1, 'L', fill=True)
        self.ln(2)

    def field(self, label, value):
        self.set_font('Arial', 'B', 9)
        self.set_text_color(50, 50, 50)
        self.write(5, f"{label}: ")
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        self.write(5, f"{str(value)}\n")

# --- 3. LOGICA DE ACCESO ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

if "password_correct" not in st.session_state:
    apply_ui_fix()
    st.title("🏥 Acceso al Sistema")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
            st.session_state["password_correct"] = True
            st.session_state["user_actual"] = u
            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
            st.rerun()
else:
    apply_ui_fix()
    with st.sidebar:
        st.header(f"Dr(a). {st.session_state['user_actual']}")
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
            st.session_state["paciente_seleccionado"] = st.selectbox("Expedientes:", lista_p)
            st.divider()
            # BOTON RESUMEN DE TURNO
            if st.button("📊 Preparar Resumen de Turno"):
                pdf_r = PEDIATRIC_PDF()
                pdf_r.add_page()
                pdf_r.section_header("Resumen de Guardia Actual")
                for pid, pdata in st.session_state["lista_pacientes"].items():
                    pdf_r.field("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                    pdf_r.field("DX", pdata['dx'])
                    pdf_r.ln(2)
                st.download_button("📥 Descargar Resumen", pdf_r.output(dest='S').encode('latin-1'), "Resumen_Turno.pdf")

    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.title(f"🧒 {pac['nombre']}")

        t = st.tabs(["ID/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]:
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'], pac['edad'], pac['sexo'] = c1.date_input("F. Nac:", pac['f_nac']), c2.text_input("Edad:", pac['edad']), c3.selectbox("Sexo:", ["M", "F"])
            st.markdown("---")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr']), s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", pac['ta']), s6.text_input("Glu:", pac['glu']), s7.text_input("Peso:", pac['peso']), s8.text_input("Talla:", pac['talla'])

        with t[1]:
            col1, col2, col3 = st.columns(3)
            pac['ahf'] = col1.text_area("Heredo-Familiares:", pac['ahf'])
            pac['vacunas'] = col1.text_area("Vacunas:", pac['vacunas'])
            pac['prenatales'] = col2.text_area("Prenatales:", pac['prenatales'])
            pac['alimentacion'] = col2.text_area("Alimentación:", pac['alimentacion'])
            pac['natales'] = col3.text_area("Natales:", pac['natales'])
            pac['desarrollo'] = col3.text_area("Desarrollo:", pac['desarrollo'])
            pac['apgar'], pac['silverman'] = col3.text_input("APGAR:", pac['apgar']), col3.text_input("Silverman:", pac['silverman'])
            pac['patologicos'] = st.text_area("Patológicos:", pac['patologicos'])

        with t[2]:
            pac['motivo'] = st.text_area("Padecimiento Actual:", pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:", pac['as_digestivo']), a2.text_area("Respiratorio:", pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a1.text_area("Cardio:", pac['as_cardio']), a2.text_area("Neuro:", pac['as_neuro'])
            pac['as_urinario'], pac['as_piel'] = a1.text_area("Urinario:", pac['as_urinario']), a2.text_area("Piel:", pac['as_piel'])
            pac['as_musculo'] = st.text_area("Músculo-Esquelético:", pac['as_musculo'])

        with t[3]:
            pac['exploracion'] = st.text_area("Exploración Física:", pac['exploracion'], height=200)

        with t[4]:
            pac['dx'], pac['plan'] = st.text_area("Diagnóstico:", pac['dx']), st.text_area("Plan:", pac['plan'])
            if st.button("🖨️ Preparar PDF Historia Clínica"):
                pdf_hc = PEDIATRIC_PDF()
                pdf_hc.add_page()
                pdf_hc.section_header("Identificación y Signos")
                pdf_hc.field("Paciente", pac['nombre'])
                pdf_hc.field("Edad", pac['edad'])
                pdf_hc.field("Signos", f"FC:{pac['fc']} FR:{pac['fr']} Sat:{pac['sat']} T:{pac['temp']} TA:{pac['ta']} P:{pac['peso']} Talla:{pac['talla']} Glu:{pac['glu']}")
                pdf_hc.section_header("Antecedentes")
                pdf_hc.field("AHF", pac['ahf'])
                pdf_hc.field("Prenatales", pac['prenatales'])
                pdf_hc.field("Natales", f"{pac['natales']} (APGAR:{pac['apgar']} SV:{pac['silverman']})")
                pdf_hc.field("Patologicos", pac['patologicos'])
                pdf_hc.section_header("Interrogatorio y Exploración")
                pdf_hc.field("Motivo", pac['motivo'])
                pdf_hc.field("Sistemas", f"Digestivo:{pac['as_digestivo']} Resp:{pac['as_resp']} Cardio:{pac['as_cardio']}")
                pdf_hc.field("Exploración", pac['exploracion'])
                pdf_hc.section_header("Diagnóstico y Plan")
                pdf_hc.field("DX", pac['dx'])
                pdf_hc.field("PLAN", pac['plan'])
                st.download_button("📥 Descargar Historia Clínica", pdf_hc.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]:
            nueva = st.text_area("Nueva nota de evolución:")
            if st.button("💾 Guardar Nota"):
                pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                st.rerun()
            if st.button("📄 Preparar PDF Notas"):
                pdf_ev = PEDIATRIC_PDF()
                pdf_ev.add_page()
                pdf_ev.section_header(f"Notas de Evolución - {pac['nombre']}")
                for n in pac["notas_evolucion"]:
                    pdf_ev.field(n['f'], n['t'])
                    pdf_ev.ln(2)
                st.download_button("📥 Descargar Evolución", pdf_ev.output(dest='S').encode('latin-1'), f"Evolucion_{pac['nombre']}.pdf")
            for n in pac["notas_evolucion"]: st.info(f"{n['f']}: {n['t']}")
