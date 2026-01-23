import streamlit as st
from fpdf import FPDF
from datetime import date, datetime

# --- 1. CONFIGURACIÓN DE USUARIOS ---
USUARIOS_AUTORIZADOS = {
    "admin": "medico2024",
    "doctor_perez": "pediatria2024"
}

def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 Acceso al Sistema Médico")
        user = st.text_input("Usuario", key="login_user")
        pwd = st.text_input("Contraseña", type="password", key="login_pwd")
        if st.button("Ingresar"):
            if user in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[user] == pwd:
                st.session_state["password_correct"] = True
                st.session_state["user_actual"] = user
                if "lista_pacientes" not in st.session_state:
                    st.session_state["lista_pacientes"] = {}
                if "paciente_seleccionado" not in st.session_state:
                    st.session_state["paciente_seleccionado"] = None
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
        return False
    return True

if check_password():
    st.set_page_config(page_title="Gestión de Turno Pediátrico", layout="wide")

    # --- 2. BARRA LATERAL: GESTIÓN DE PACIENTES ---
    with st.sidebar:
        st.write(f"👨‍⚕️ Médico: **{st.session_state['user_actual']}**")
        if st.button("Cerrar Sesión"):
            del st.session_state["password_correct"]
            st.rerun()
        
        st.divider()
        st.header("👥 Pacientes en Turno")
        
        if st.button("➕ AGREGAR NUEVO PACIENTE"):
            nuevo_id = f"Paciente {len(st.session_state['lista_pacientes']) + 1}"
            st.session_state["lista_pacientes"][nuevo_id] = {
                "nombre": "", "f_nac": date(2020,1,1), "tutor": "",
                "peso": "", "talla": "", "fc": "", "temp": "",
                "notas_evolucion": [], "dx": "", "plan": "", "antecedentes": "",
                "motivo": "", "exploracion": ""
            }
            st.session_state["paciente_seleccionado"] = nuevo_id
            st.rerun()

        nombres_pacientes = list(st.session_state["lista_pacientes"].keys())
        if nombres_pacientes:
            seleccion = st.selectbox("Seleccionar Paciente:", nombres_pacientes, 
                                     index=nombres_pacientes.index(st.session_state["paciente_seleccionado"]) if st.session_state["paciente_seleccionado"] in nombres_pacientes else 0)
            st.session_state["paciente_seleccionado"] = seleccion
        
        st.divider()
        # --- NUEVO BOTÓN: RESUMEN DE TURNO ---
        st.subheader("Reportes Finales")
        if st.button("📑 GENERAR RESUMEN DE TURNO"):
            if st.session_state["lista_pacientes"]:
                pdf_turno = FPDF()
                pdf_turno.add_page()
                pdf_turno.set_font("Arial", 'B', 16)
                pdf_turno.cell(0, 10, f"RESUMEN DE TURNO - {date.today()}", ln=True, align='C')
                pdf_turno.set_font("Arial", size=10)
                pdf_turno.cell(0, 10, f"Medico responsable: {st.session_state['user_actual']}", ln=True)
                pdf_turno.ln(5)

                for pid, pdata in st.session_state["lista_pacientes"].items():
                    nombre_p = pdata['nombre'] if pdata['nombre'] else pid
                    pdf_turno.set_font("Arial", 'B', 12)
                    pdf_turno.cell(0, 10, f"PACIENTE: {nombre_p}", ln=True)
                    pdf_turno.set_font("Arial", size=10)
                    pdf_turno.multi_cell(0, 7, f"DX: {pdata['dx']}\nPLAN: {pdata['plan']}")
                    pdf_turno.ln(3)
                    pdf_turno.cell(0, 0, "", "T", ln=True) # Línea divisoria
                
                pdf_turno.output("Resumen_Turno_Completo.pdf")
                st.sidebar.success("✅ Resumen de turno generado.")
            else:
                st.sidebar.warning("No hay pacientes registrados.")

    # --- 3. CARGA DE DATOS DEL PACIENTE SELECCIONADO ---
    if not st.session_state["lista_pacientes"]:
        st.info("Haga clic en 'Agregar Nuevo Paciente' para comenzar.")
        st.stop()

    p_id = st.session_state["paciente_seleccionado"]
    p_data = st.session_state["lista_pacientes"][p_id]

    st.title(f"🏥 Expediente: {p_data['nombre'] if p_data['nombre'] else p_id}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👤 Identificación", "👶 Antecedentes", "🩺 Interrogatorio", 
        "🔍 Exploración", "📝 Plan y Dx", "📈 Evolución"
    ])

    with tab1:
        st.subheader("Ficha de Identificación")
        p_data['nombre'] = st.text_input("Nombre Completo:", value=p_data['nombre'])
        c1, c2 = st.columns(2)
        p_data['f_nac'] = c1.date_input("Fecha de Nacimiento:", value=p_data['f_nac'])
        p_data['tutor'] = c2.text_input("Padre o Tutor:", value=p_data['tutor'])
        st.divider()
        st.subheader("Somatometría")
        cs1, cs2, cs3 = st.columns(3)
        p_data['peso'] = cs1.text_input("Peso (kg):", value=p_data['peso'])
        p_data['talla'] = cs2.text_input("Talla (cm):", value=p_data['talla'])
        p_data['temp'] = cs3.text_input("Temp (°C):", value=p_data['temp'])

    with tab2:
        p_data['antecedentes'] = st.text_area("Heredofamiliares y Perinatales:", value=p_data['antecedentes'])

    with tab3:
        p_data['motivo'] = st.text_area("Padecimiento actual:", value=p_data['motivo'])

    with tab4:
        p_data['exploracion'] = st.text_area("Hallazgos físicos:", value=p_data['exploracion'])

    with tab5:
        p_data['dx'] = st.text_area("Diagnóstico:", value=p_data['dx'])
        p_data['plan'] = st.text_area("Plan Terapéutico:", value=p_data['plan'])

    with tab6:
        st.subheader("Notas de Evolución")
        nueva_n = st.text_area("Escribir nota:", key=f"new_note_{p_id}")
        if st.button("➕ Guardar Nota"):
            if nueva_n:
                ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                p_data["notas_evolucion"].insert(0, {"fecha": ahora, "texto": nueva_n})
                st.rerun()
        for n in p_data["notas_evolucion"]:
            st.info(f"📅 {n['fecha']}\n\n{n['texto']}")

    # --- 5. PDF INDIVIDUAL ---
    if st.button("💾 GENERAR PDF DE ESTE PACIENTE"):
        if p_data['nombre']:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"HISTORIA CLINICA - {p_data['nombre']}", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.ln(5)
            pdf.cell(0, 8, f"Fecha: {date.today()} | Medico: {st.session_state['user_actual']}", ln=True)
            pdf.ln(5)
            pdf.multi_cell(0, 7, f"DIAGNOSTICO: {p_data['dx']}\nPLAN: {p_data['plan']}")
            pdf.output(f"HC_{p_data['nombre']}.pdf")
            st.success("PDF individual generado.")

