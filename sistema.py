import streamlit as st
from fpdf import FPDF
from datetime import date, datetime

# --- 1. GESTIÓN DE USUARIOS Y REGISTRO ---
if "db_usuarios" not in st.session_state:
    st.session_state["db_usuarios"] = {"admin": "medico2024"}

def login_registro():
    if "password_correct" not in st.session_state:
        st.title("🏥 Sistema de Expedientes Pediátricos Avanzado")
        menu = ["Iniciar Sesión", "Registrarse"]
        choice = st.radio("Seleccione una opción", menu, horizontal=True)

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
            new_user = st.text_input("Cree un Usuario")
            new_pwd = st.text_input("Cree una Contraseña", type="password")
            if st.button("Crear Cuenta"):
                if new_user and new_pwd:
                    st.session_state["db_usuarios"][new_user] = new_pwd
                    st.success("✅ Cuenta creada.")
        return False
    return True

if login_registro():
    st.set_page_config(page_title="Expediente Pediátrico Avanzado", layout="wide")

    # --- 2. BARRA LATERAL ---
    with st.sidebar:
        st.write(f"👨‍⚕️ Usuario: **{st.session_state['user_actual']}**")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        st.divider()
        if st.button("➕ AGREGAR NUEVO PACIENTE"):
            p_id = f"PAC-{datetime.now().strftime('%H%M%S')}"
            st.session_state["lista_pacientes"][p_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "sexo": "M",
                "peso": "", "talla": "", "fc": "", "fr": "", "temp": "", "sat": "",
                # --- ANTECEDENTES EXTENSOS ---
                "ahf": "", "prenatales": "", "natales": "", "neonatales": "",
                "apgar": "", "silverman": "", "tamiz": "", "vacunas": "",
                "alimentacion": "", "desarrollo": "", "habitos": "", "patologicos": "",
                # --- CONSULTA ---
                "motivo": "", "exploracion": "", "dx": "", "plan": "",
                "notas_evolucion": []
            }
            st.session_state["paciente_seleccionado"] = p_id
            st.rerun()

        lista = list(st.session_state["lista_pacientes"].keys())
        if lista:
            st.session_state["paciente_seleccionado"] = st.selectbox("Expediente:", lista)

    # --- 3. CUERPO MÉDICO ---
    if st.session_state.get("paciente_seleccionado"):
        p = st.session_state["lista_pacientes"][st.session_state["paciente_seleccionado"]]

        tabs = st.tabs(["👤 ID", "📋 ANTECEDENTES", "🩺 CONSULTA", "🔍 EXPLORACIÓN", "📝 DX/PLAN", "📈 EVOLUCIÓN"])

        with tabs[0]: # IDENTIFICACIÓN
            st.subheader("Ficha de Identificación")
            p['nombre'] = st.text_input("Nombre Completo:", value=p['nombre'])
            c1, c2, c3, c4 = st.columns(4)
            p['f_nac'] = c1.date_input("F. Nac:", value=p['f_nac'])
            p['sexo'] = c2.selectbox("Sexo:", ["M", "F"], index=0 if p['sexo']=="M" else 1)
            p['peso'] = c3.text_input("Peso (kg):", value=p['peso'])
            p['talla'] = c4.text_input("Talla (cm):", value=p['talla'])

        with tabs[1]: # ANTECEDENTES EXTENSOS
            st.subheader("Historia Clínica Detallada")
            sub1, sub2, sub3 = st.columns(3)
            
            with sub1:
                st.write("**Heredo-Familiares**")
                p['ahf'] = st.text_area("Diabetes, HTA, Cáncer, Malformaciones, Cardiopatías:", value=p['ahf'])
                st.write("**Prenatales**")
                p['prenatales'] = st.text_area("Gesta, control prenatal, infecciones, amenazas de aborto:", value=p['prenatales'])

            with sub2:
                st.write("**Perinatales (Parto)**")
                p['natales'] = st.text_area("Tipo parto, semanas gestación, fórceps, anestesia:", value=p['natales'])
                st.write("**Neonatales**")
                c_n1, c_n2 = st.columns(2)
                p['apgar'] = c_n1.text_input("APGAR:", value=p['apgar'])
                p['silverman'] = c_n2.text_input("Silverman:", value=p['silverman'])
                p['neonatales'] = st.text_area("Ictericia, apnea, hospitalización previa:", value=p['neonatales'])

            with sub3:
                st.write("**Desarrollo y Nutrición**")
                p['desarrollo'] = st.text_area("Sostén cefálico, marcha, lenguaje, dentición:", value=p['desarrollo'])
                p['alimentacion'] = st.text_area("Lactancia materna, ablactación, dieta actual:", value=p['alimentacion'])
                p['vacunas'] = st.text_area("Esquema de vacunación, Tamiz:", value=p['vacunas'])

            st.divider()
            st.write("**Antecedentes Personales Patológicos**")
            p['patologicos'] = st.text_area("Quirúrgicos, alérgicos, transfusionales, traumáticos:", value=p['patologicos'])

        with tabs[2]: # INTERROGATORIO
            p['motivo'] = st.text_area("Motivo de consulta y Padecimiento Actual (semiología):", value=p['motivo'])

        with tabs[3]: # EXPLORACIÓN
            p['exploracion'] = st.text_area("Cabeza, Cuello, Tórax, Abdomen, Genitales, Extremidades:", value=p['exploracion'])

        with tabs[4]: # DIAGNÓSTICO Y PLAN
            p['dx'] = st.text_area("Impresión Diagnóstica:", value=p['dx'])
            p['plan'] = st.text_area("Tratamiento, dosis, frecuencia y duración:", value=p['plan'])

        with tabs[5]: # EVOLUCIÓN
            nueva = st.text_area("Nueva Nota de Evolución:")
            if st.button("Guardar Nota"):
                if nueva:
                    p["notas_evolucion"].insert(0, {"f": datetime.now().strftime("%d/%m/%Y %H:%M"), "t": nueva})
                    st.rerun()
            for n in p["notas_evolucion"]:
                st.info(f"📅 {n['f']}\n{n['t']}")

    # --- 4. REPORTES ---
    st.sidebar.divider()
    if st.sidebar.button("💾 GENERAR RESUMEN DE TURNO"):
        st.sidebar.success("Generando reporte de todos los pacientes del turno...")

