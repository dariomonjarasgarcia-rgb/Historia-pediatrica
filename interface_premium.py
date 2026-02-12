import streamlit as st

def cargar_estilo_hospital():
    """Inyecta el ADN visual de un hospital de primer nivel"""
    st.markdown("""
        <style>
        /* Importar fuente moderna */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* Fondo y Tipografía */
        .stApp {
            background-color: #F1F5F9;
            font-family: 'Inter', sans-serif;
        }

        /* Tarjetas blancas para el contenido */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            padding: 2rem !important;
            margin-bottom: 1rem;
        }

        /* Sidebar elegante */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        /* Botones estilo 'Premium Clinic' */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
            border: none;
        }
        
        /* Botón de acción principal (Nuevo Paciente) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        }

        /* Estilo de las pestañas (Tabs) */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #E2E8F0;
            border-radius: 6px 6px 0 0;
            padding: 8px 20px;
            color: #475569;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563EB !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar_hospital(nombre_doctor="Dr(a). D"):
    """Dibuja el menú lateral estilizado"""
    with st.sidebar:
        st.markdown(f"### 🏥 Unidad Pediátrica\n**{nombre_doctor}**")
        st.divider()
        st.button("➕ NUEVO PACIENTE", use_container_width=True, type="primary")
        st.divider()
        st.caption("Gestión de Expedientes")
