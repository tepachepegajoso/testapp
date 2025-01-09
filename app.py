import streamlit as st
import pandas as pd
import os

# Título de la aplicación
st.title("Gestión y Análisis de Datos con Streamlit")

# Ruta del archivo CSV (en la misma carpeta que el script)
CSV_PATH = "testc.csv"  # Cambia el nombre a tu archivo CSV

# Función para cargar el CSV
def cargar_csv():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        st.error("El archivo CSV no se encontró en la misma carpeta que el script.")
        return pd.DataFrame()

# Función para guardar el CSV
def guardar_csv(df):
    df.to_csv(CSV_PATH, index=False)
    st.success("¡Cambios guardados en el archivo CSV!")

# Inicializar el estado del DataFrame en session_state
if "data" not in st.session_state:
    st.session_state.data = cargar_csv()

# Manejo de datos faltantes
df = st.session_state.data
df.fillna("", inplace=True)

# Crear menú con opciones
menu = ["Edición de Datos", "Filtrar y Graficar"]
opcion = st.sidebar.selectbox("Seleccione una opción", menu)

if opcion == "Edición de Datos":
    # Edición de datos
    st.subheader("Edición del Archivo CSV")

    habilitar_edicion = st.checkbox("Habilitar edición del CSV")

    if not df.empty:
        st.write("Datos del archivo CSV cargado:")

        if habilitar_edicion:
            # Mostrar los datos en un editor interactivo
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

            # Botón para guardar los cambios
            if st.button("Guardar cambios"):
                st.session_state.data = edited_df  # Actualizar el estado con los cambios
                guardar_csv(edited_df)
        else:
            # Mostrar los datos sin opción de editar
            st.dataframe(st.session_state.data, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar. Asegúrate de que el archivo CSV existe en la misma carpeta.")

elif opcion == "Filtrar y Graficar":
    # Filtrar y graficar datos
    st.subheader("Filtrar Datos y Generar Gráficas")

    if not df.empty:
        # Seleccionar mes
        meses = df["mes"].unique()
        mes_seleccionado = st.selectbox("Seleccione un mes", sorted(meses))

        # Filtrar datos por mes
        datos_filtrados = df[df["mes"] == mes_seleccionado]

        # Calcular horas invertidas por actividad
        resumen_actividades = datos_filtrados.groupby("actividad")["horas"].sum().reset_index()

        st.write("Resumen de horas por actividad en el mes seleccionado:")
        st.dataframe(resumen_actividades, use_container_width=True)

        # Selección de tipo de gráfica
        tipo_grafica = st.radio("Seleccione el tipo de gráfica", ["Barras", "Pastel"])

        if tipo_grafica == "Barras":
            st.bar_chart(resumen_actividades, x="actividad", y="horas", use_container_width=True)
        elif tipo_grafica == "Pastel":
            import plotly.express as px

            # Crear gráfica de pastel
            fig = px.pie(
                resumen_actividades,
                names="actividad",
                values="horas",
                title="Distribución de horas por actividad",
                hole=0.3,  # Gráfica tipo donut
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para filtrar o graficar.")




