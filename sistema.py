import streamlit as st
from fpdf import FPDF
from datetime import date, datetime

# --- 1. GESTIÓN DE USUARIOS Y REGISTRO ---
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
                    st.success("✅ Cuenta creada correctamente.")
        return False
    return True

if login_registro():
    st.set_page_config(page_title="Expediente Pediátrico Avanzado", layout="wide")

    # --- 2. BARRA LATERAL ---
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
                # Aparatos y Sistemas
                "as_digestivo": "", "as_resp": "", "as_cardio": "", "as_neuro": "", "as_urinario": "", "as_musculo": "", "as_piel": "",
                "dx": "", "plan": "", "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()

        lista = list(st.session_state["lista_pacientes"].keys())
        if lista:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista)

    # --- 3. CUERPO MÉDICO ---
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
            st.subheader("🩺 Signos Vitales y Somatometría")
            s1, s2, s3, s4 = st.columns(4)
            p['fc'] = s1.text_input("FC (lpm):", value=p['fc'])
            p['fr'] = s2.text_input("FR (rpm):", value=p['fr'])
            p['sat'] = s3.text_input("SatO2 (%):", value=p['sat'])
            p['temp'] = s4.text_input("Temp (°C):", value=p['temp'])
            
            s5, s6, s7, s8 = st.columns(4)
            p['ta'] = s5.text_input("Tensión Arterial (mmHg):", value=p['ta'])
            p['glu'] = s6.text_input("Glucosa (mg/dL):", value=p['glu'])
            p['peso'] = s7.text_input("Peso (kg):", value=p['peso'])
            p['talla'] = s8.text_input("Talla (cm):", value=p['talla'])

        with tabs[1]: # ANTECEDENTES (DISPOSICIÓN HORIZONTAL)
            st.subheader("Historia Clínica: Antecedentes")
            col1, col2, col3 = st.columns(3)
            with col1:
                p['ahf'] = st.text_area("Heredo-Familiares:", value=p['ahf'], height=150)
                p['vacunas'] = st.text_area("Inmunizaciones/Tamiz:", value=p['vacunas'], height=150)
            with col2:
                p['prenatales'] = st.text_area("Prenatales (Embarazo):", value=p['prenatales'], height=150)
                p['alimentacion'] = st.text_area("Alimentación (Lactancia/Dieta):", value=p['alimentacion'], height=150)
            with col3:
                p['natales'] = st.text_area("Natales (Parto):", value=p['natales'], height=100)
                c_n1, c_n2 = st.columns(2)
                p['apgar'] = c_n1.text_input("APGAR:", value=p['apgar'])
                p['silverman'] = c_n2.text_input("Silverman:", value=p['silverman'])
                p['desarrollo'] = st.text_area("Desarrollo Psicomotor:", value=p['desarrollo'], height=100)

            p['patologicos'] = st.text_area("Personales Patológicos (Alergias, Quirúrgicos, Traumáticos):", value=p['patologicos'])

        with tabs[2]: # APARATOS Y SISTEMAS (CASILLAS INDIVIDUALES)
            st.subheader("Interrogatorio por Aparatos y Sistemas")
            p['motivo'] = st.text_area("Padecimiento Actual (Semiología):", value=p['motivo'])
            st.divider()
            
            a1, a2 = st.columns(2)
            p['as_digestivo'] = a1.text_area("Aparato Digestivo:", value=p['as_digestivo'])
            p['as_resp'] = a2.text_area("Aparato Respiratorio:", value=p['as_resp'])
            
            a3, a4 = st.columns(2)
            p['as_cardio'] = a3.text_area("Aparato Cardiovascular:", value=p['as_cardio'])
            p['as_neuro'] = a4.text_area("Sistema Nervioso:", value=p['as_neuro'])
            
            a5, a6 = st.columns(2)
            p['as_urinario'] = a5.text_area("Aparato Genitourinario:", value=p['as_urinario'])
            p['as_piel'] = a6.text_area("Piel y Faneras:", value=p['as_piel'])
            
            p['as_musculo'] = st.text_area("Sistema Músculo-Esquelético:", value=p['as_musculo'])

        with tabs[3]: # EXPLORACIÓN
            p['exploracion'] = st.text_area("Exploración Física Céfalo-Caudal:", value=p['exploracion'], height=300)

        with tabs[4]: # DIAGNÓSTICO Y PLAN
            p['dx'] = st.text_area("Impresión Diagnóstica:", value=p['dx'])
            p['plan'] = st.text_area("Plan Terapéutico e Indicaciones:", value=p['plan'])

        with tabs[5]: # EVOLUCIÓN
            nueva = st.text_area("Nueva Nota:")
            if st.button("Guardar Nota"):
                if nueva:
                    p["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            for n in p["notas_evolucion"]:
                st.info(f"📅 {n['f']}\n{n['t']}")

    # --- 4. BOTONES DE PDF ---
    st.sidebar.divider()
    if st.sidebar.button("💾 GENERAR RESUMEN DE TURNO"):
        st.sidebar.success("Generando reporte PDF consolidado...")


