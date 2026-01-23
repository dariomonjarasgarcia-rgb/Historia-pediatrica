import streamlit as st
from fpdf import FPDF
from datetime import date

st.set_page_config(page_title="Expediente Pediátrico Integral", layout="wide")

# Estilo visual médico
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e9ecef; 
        border-radius: 5px; 
        padding: 8px 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 Historia Clínica Pediátrica Integral")

# --- BARRA LATERAL: SOMATOMETRÍA Y SIGNOS VITALES ---
with st.sidebar:
    st.header("📊 Somatometría")
    peso = st.text_input("Peso (kg):")
    talla = st.text_input("Talla (cm):")
    p_cef = st.text_input("Perímetro Cefálico (cm):")
    p_abd = st.text_input("Perímetro Abdominal (cm):")
    st.divider()
    st.header("🌡️ Signos Vitales")
    temp = st.text_input("Temperatura (°C):")
    fc = st.text_input("FC (lpm):")
    fr = st.text_input("FR (rpm):")
    sat = st.text_input("Saturación O2 (%):")
    ta = st.text_input("Tensión Arterial (mmHg):")

# --- CUERPO PRINCIPAL (TODOS LOS APARTADOS) ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👤 Identificación", 
    "👶 Antecedentes", 
    "🩺 Interrogatorio", 
    "🔍 Exploración", 
    "🔬 Auxiliares", 
    "📝 Plan y Dx"
])

with tab1:
    st.subheader("Ficha de Identificación")
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Nombre del Paciente:")
    f_nac = c2.date_input("Fecha de Nacimiento:", value=date(2020,1,1))
    sexo = c3.selectbox("Sexo:", ["Masculino", "Femenino"])
    tutor = c1.text_input("Nombre del Padre/Madre/Tutor:")
    parentesco = c2.text_input("Parentesco:")
    telefono = c3.text_input("Teléfono:")
    domicilio = st.text_area("Domicilio:")

with tab2:
    col_ant1, col_ant2 = st.columns(2)
    with col_ant1:
        st.subheader("Antecedentes Perinatales")
        gestas = st.text_input("No. Gesta / Para / Abortos:")
        evol_preg = st.text_area("Evolución del embarazo:")
        tipo_p = st.selectbox("Tipo de Parto:", ["Eutócico", "Cesárea", "Fórceps"])
        apgar = st.text_input("APGAR (1'/5'):")
        silverman = st.text_input("Silverman-Andersen:")
        hosp_rn = st.text_area("Hospitalización del RN / Complicaciones:")
    with col_ant2:
        st.subheader("Antecedentes Familiares")
        st.write("Marque antecedentes positivos:")
        c_ahf1, c_ahf2 = st.columns(2)
        diab = c_ahf1.checkbox("Diabetes Mellitus")
        hta = c_ahf2.checkbox("Hipertensión Arterial")
        neoplasia = c_ahf1.checkbox("Cáncer / Neoplasias")
        alergia = c_ahf2.checkbox("Alergias Familiares")
        ahf_detalles = st.text_area("Detalle de AHF y parentesco:")

with tab3:
    st.subheader("Interrogatorio por Aparatos y Sistemas")
    col_sys1, col_sys2 = st.columns(2)
    with col_sys1:
        motivo = st.text_area("Motivo de consulta / Padecimiento actual:")
        digestivo = st.text_area("Aparato Digestivo:")
        respiratorio = st.text_area("Aparato Respiratorio:")
    with col_sys2:
        cardio = st.text_area("Aparato Cardiovascular:")
        neuro = st.text_area("Neurológico y Desarrollo Psicomotor:")
        inmuno = st.text_area("Inmunizaciones (Esquema de vacunas):")

with tab4:
    st.subheader("Exploración Física Detallada")
    habitus = st.text_area("Habitus Exterior:")
    cabeza = st.text_area("Cabeza y Cuello (Fontanelas, ojos, oídos, faringe):")
    torax = st.text_area("Tórax (Campos pulmonares, ruidos cardiacos):")
    abdomen = st.text_area("Abdomen (Masas, visceromegalias, ruidos):")
    extremidades = st.text_area("Extremidades y Columna:")
    genitales = st.text_area("Genitales y Ano:")

with tab5:
    st.subheader("Auxiliares de Diagnóstico")
    laboratorio = st.text_area("Resultados de Laboratorio:")
    gabinete = st.text_area("Estudios de Gabinete (RX, USG, etc.):")

with tab6:
    st.subheader("Conclusiones Médicas")
    dx = st.text_area("Impresión Diagnóstica:")
    tratamiento = st.text_area("Plan Terapéutico y Medicación:")
    pronostico = st.text_input("Pronóstico:")
    
    if st.button("💾 GENERAR EXPEDIENTE PDF"):
        if nombre:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "HISTORIA CLINICA PEDIATRICA", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.ln(5)
            # Resumen de datos en el PDF
            pdf.cell(0, 8, f"PACIENTE: {nombre} | SEXO: {sexo} | FECHA NAC: {f_nac}", ln=True)
            pdf.cell(0, 8, f"PESO: {peso}kg | TALLA: {talla}cm | FC: {fc} | TEMP: {temp}", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "DIAGNOSTICO Y PLAN", ln=True)
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 7, f"Dx: {dx}")
            pdf.multi_cell(0, 7, f"Plan: {tratamiento}")
            
            nombre_f = f"HC_{nombre.replace(' ', '_')}.pdf"
            pdf.output(nombre_f)
            st.success(f"✅ ¡Expediente de {nombre} guardado!")
        else:
            st.error("Error: El nombre es obligatorio.")
