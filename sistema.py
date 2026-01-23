import streamlit as st
from fpdf import FPDF
from datetime import date, datetime
import io

# --- 1. CONFIGURACIÓN DE PÁGINA Y FUERZA VISUAL ---
st.set_page_config(page_title="Expediente Pediátrico Pro", layout="wide")

def apply_high_contrast_design():
    st.markdown("""
        <style>
        /* FORZADO DE CONTRASTE TOTAL */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Forzar que todos los textos sean negros */
        h1, h2, h3, p, label, .stMarkdown, .stSelectbox, .stTextInput, .stTextArea {
            color: #000000 !important;
        }

        /* Estilo de los campos de entrada (Inputs) */
        input, textarea {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
            border: 2px solid #007bff !important;
        }

        /* Tabs (Pestañas) - Color Azul Pediátrico */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #FFFFFF !important;
            border-bottom: 2px solid #007bff;
        }
        .stTabs [data-baseweb="tab"] {
            color: #000000 !important;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #007bff !important;
            color: #FFFFFF !important;
            border-radius: 5px 5px 0 0;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA !important;
            border-right: 2px solid #007bff;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. CLASE PDF PROFESIONAL ---
class PEDIATRIC_PDF(FPDF):
    def header(self):
        self.set_fill_color(0, 123, 255) # Azul institucional
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Arial', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'EXPEDIENTE CLINICO PEDIATRICO', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f'Fecha de Emision: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')
        self.ln(20)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.set_text_color(0, 51, 102)
        self.cell(0, 8, f" {label}", 0, 1, 'L', fill=True)
        self.ln(2)

    def data_row(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(50, 50, 50)
        self.write(6, f"{label}: ")
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.write(6, f"{value}\n")

# --- 3. LÓGICA DE USUARIOS ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2026"}

if "password_correct" not in st.session_state:
    apply_high_contrast_design()
    st.title("🔐 Acceso Médicos")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u in st.session_state["db_usuarios"] and st.session_state["db_usuarios"][u] == p:
            st.session_state["password_correct"] = True
            st.session_state["user_actual"] = u
            if "lista_pacientes" not in st.session_state: st.session_state["lista_pacientes"] = {}
            st.rerun()
else:
    apply_high_contrast_design()
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("👨‍⚕️ Menú")
        if st.button("➕ NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "sexo": "M", "edad": "",
                "peso": "", "talla": "", "fc": "", "fr": "", "sat": "", "glu": "", "ta": "", "temp": "",
                "ahf": "", "prenatales": "", "natales": "", "neonatales": "", "apgar": "", "silverman": "",
                "vacunas": "", "alimentacion": "", "desarrollo": "", "patologicos": "", "motivo": "",
                "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "", "as_urinario": "", "as_piel": "", "as_musculo": "",
                "exploracion": "", "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()
        
        lista_p = list(st.session_state["lista_pacientes"].keys())
        if lista_p:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expedientes:", lista_p)
            
            # BOTÓN RESUMEN DE TURNO PDF
            pdf_res = PEDIATRIC_PDF()
            pdf_res.add_page()
            pdf_res.section_title("RESUMEN DE GUARDIA")
            for pid, pdata in st.session_state["lista_pacientes"].items():
                pdf_res.data_row("PACIENTE", f"{pdata['nombre']} ({pdata['edad']})")
                pdf_res.data_row("DX", pdata['dx'])
                pdf_res.ln(2)
            res_b = pdf_res.output(dest='S').encode('latin-1')
            st.download_button("📊 Descargar Resumen Turno", res_b, "Resumen_Turno.pdf")

    # --- CUERPO MÉDICO ---
    if st.session_state.get("paciente_seleccionado"):
        pac = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]
        st.markdown(f"## 📋 Paciente: {pac['nombre']}")

        t = st.tabs(["Ficha/Signos", "Antecedentes", "Sistemas", "Exploración", "DX/Plan", "Evolución"])

        with t[0]:
            pac['nombre'] = st.text_input("Nombre Completo:", value=pac['nombre'])
            c1, c2, c3 = st.columns(3)
            pac['f_nac'] = c1.date_input("F. Nac:", value=pac['f_nac'])
            pac['edad'] = c2.text_input("Edad:", value=pac['edad'])
            pac['sexo'] = c3.selectbox("Sexo:", ["M", "F"], index=0 if pac['sexo']=="M" else 1)
            st.markdown("---")
            s1, s2, s3, s4 = st.columns(4)
            pac['fc'], pac['fr'], pac['sat'], pac['temp'] = s1.text_input("FC:", pac['fc']), s2.text_input("FR:", pac['fr']), s3.text_input("SatO2:", pac['sat']), s4.text_input("Temp:", pac['temp'])
            s5, s6, s7, s8 = st.columns(4)
            pac['ta'], pac['glu'], pac['peso'], pac['talla'] = s5.text_input("TA:", pac['ta']), s6.text_input("Glu:", pac['glu']), s7.text_input("Peso:", pac['peso']), s8.text_input("Talla:", pac['talla'])

        with t[1]:
            c1, c2, c3 = st.columns(3)
            pac['ahf'], pac['vacunas'] = c1.text_area("AHF:", pac['ahf']), c1.text_area("Vacunas:", pac['vacunas'])
            pac['prenatales'], pac['alimentacion'] = c2.text_area("Prenatales:", pac['prenatales']), c2.text_area("Alimentación:", pac['alimentacion'])
            pac['natales'], pac['desarrollo'] = c3.text_area("Natales:", pac['natales']), c3.text_area("Desarrollo:", pac['desarrollo'])
            pac['patologicos'] = st.text_area("Patológicos:", pac['patologicos'])

        with t[2]:
            pac['motivo'] = st.text_area("Padecimiento Actual:", pac['motivo'])
            a1, a2 = st.columns(2)
            pac['as_digestivo'], pac['as_resp'] = a1.text_area("Digestivo:", pac['as_digestivo']), a2.text_area("Resp:", pac['as_resp'])
            pac['as_cardio'], pac['as_neuro'] = a3, a4 = a1.text_area("Cardio:", pac['as_cardio']), a2.text_area("Neuro:", pac['as_neuro'])
            pac['as_urinario'], pac['as_piel'] = a1.text_area("Urinario:", pac['as_urinario']), a2.text_area("Piel:", pac['as_piel'])

        with t[3]:
            pac['exploracion'] = st.text_area("Exploración Física:", pac['exploracion'], height=200)

        with t[4]:
            pac['dx'], pac['plan'] = st.text_area("Diagnóstico:", pac['dx']), st.text_area("Plan:", pac['plan'])
            if st.button("🖨️ Generar PDF Historia Clínica"):
                pdf_hc = PEDIATRIC_PDF()
                pdf_hc.add_page()
                pdf_hc.section_title("IDENTIFICACION")
                pdf_hc.data_row("Nombre", pac['nombre'])
                pdf_hc.data_row("Edad", pac['edad'])
                pdf_hc.section_title("SIGNOS VITALES")
                pdf_hc.data_row("Signos", f"FC:{pac['fc']} FR:{pac['fr']} Sat:{pac['sat']} T:{pac['temp']} TA:{pac['ta']} P:{pac['peso']}")
                pdf_hc.section_title("DIAGNOSTICO Y PLAN")
                pdf_hc.data_row("DX", pac['dx'])
                pdf_hc.data_row("PLAN", pac['plan'])
                st.download_button("📥 Descargar Archivo", pdf_hc.output(dest='S').encode('latin-1'), f"HC_{pac['nombre']}.pdf")

        with t[5]:
            nueva = st.text_area("Nota nueva:")
            if st.button("Guardar Nota"):
                pac["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                st.rerun()
            for n in pac["notas_evolucion"]: st.info(f"{n['f']}: {n['t']}")
