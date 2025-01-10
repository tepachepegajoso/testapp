import streamlit as st
import pandas as pd
import os
import plotly.express as px
from streamlit_option_menu import option_menu

# Título de la aplicación
st.title("Gestión de Tiempos y Proyectos")

# Ruta del archivo CSV (en la misma carpeta que el script)
CSV_PATH = "archivo.csv"  # Cambia el nombre a tu archivo CSV

# Función para cargar el CSV
def cargar_csv():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        st.error("El archivo CSV no se encontró en la misma carpeta que el script.")
        return pd.DataFrame()

# Inicializar el estado del DataFrame en session_state
if "data" not in st.session_state:
    st.session_state.data = cargar_csv()

# Manejo de datos faltantes
df = st.session_state.data
df.fillna("", inplace=True)

# Verificar que existan datos
if df.empty:
    st.warning("No hay datos para mostrar. Asegúrate de que el archivo CSV existe en la misma carpeta.")
else:
    # Crear un menú usando streamlit-option-menu
    with st.sidebar:
        menu = option_menu(
            menu_title="Menú",
            options=["Filtrar datos", "Ver recursos", "Editar CSV"],
            icons=["filter", "eye", "pencil"],
            menu_icon="cast",
            default_index=0,
        )

    if menu == "Filtrar datos":
        # Filtro principal: Mes
        st.subheader("Filtrado de Datos")
        meses = df["Mes"].unique()
        mes_seleccionado = st.selectbox("Seleccione un mes", sorted(meses))

        datos_filtrados_mes = df[df["Mes"] == mes_seleccionado]

        # Filtro secundario: Actividades (múltiples)
        actividades = datos_filtrados_mes["Actividad"].unique()
        actividades_seleccionadas = st.multiselect("Seleccione actividades", sorted(actividades))

        # Si se seleccionan actividades, mostrar las métricas y generar la gráfica
        if actividades_seleccionadas:
            total_horas_por_actividad = []

            # Mostrar las horas por actividad
            for actividad in actividades_seleccionadas:
                st.write(f"### Actividad: {actividad}")
                datos_actividad = datos_filtrados_mes[datos_filtrados_mes["Actividad"] == actividad]

                # Resumen de horas
                total_horas = datos_actividad["HR asignadas"].sum()
                st.metric(label=f"Horas invertidas en {actividad}", value=f"{total_horas} horas")

                # Agregar a la lista para el gráfico combinado
                total_horas_por_actividad.append((actividad, total_horas))

                # Mostrar proyectos y descripciones con el color de fondo intercalado
                if st.checkbox(f"Mostrar proyectos y descripciones para {actividad}", key=f"check_{actividad}"):
                    proyectos_descripciones = datos_actividad[["Proyecto", "Descripción"]].drop_duplicates()

                    if not proyectos_descripciones.empty:
                        html_content = """<style>
                                          table {width: 100%;}
                                          th, td {border: 1px solid #ddd; padding: 8px;}
                                          tr:nth-child(even) {background-color: #9b2148; color: white;}
                                          tr:nth-child(odd) {background-color: #a87f2f; color: white;}
                                          </style><table>"""
                        # Agregar cabecera de la tabla
                        html_content += "<tr><th>Proyecto</th><th>Descripción</th></tr>"
                        for _, row in proyectos_descripciones.iterrows():
                            html_content += f"<tr><td>{row['Proyecto']}</td><td>{row['Descripción']}</td></tr>"
                        html_content += "</table>"
                        st.markdown(html_content, unsafe_allow_html=True)

            # Mostrar gráfico combinado en la parte inferior de las actividades seleccionadas
            if total_horas_por_actividad:
                st.write("### Resumen de todas las actividades seleccionadas")
                resumen_df = pd.DataFrame(total_horas_por_actividad, columns=["Actividad", "HR asignadas"])

                # Crear la gráfica de barras con estilo de barras delgadas
                fig = px.bar(resumen_df, x="Actividad", y="HR asignadas", 
                             labels={"HR asignadas": "Horas Asignadas"}, 
                             title="Horas Asignadas por Actividad")

                # Ajustar las barras para que sean más delgadas
                fig.update_traces(marker=dict(line=dict(width=0)), opacity=0.7)

                # Reducir el gap entre barras para hacerlas más estrechas
                fig.update_layout(
                    barmode='group', 
                    xaxis_tickangle=-45, 
                    bargap=0.05  # Ajusta este valor para hacer las barras más estrechas
                )

                # Mostrar el gráfico en Streamlit
                st.plotly_chart(fig, use_container_width=True)

    elif menu == "Ver recursos":
        # Mostrar columna "Recurso" con datos asociados solo con clave correcta
        st.subheader("Opciones avanzadas: Ver Recursos")

        # Filtros aplicados al igual que en "Filtrar datos"
        meses = df["Mes"].unique()
        mes_seleccionado = st.selectbox("Seleccione un mes", sorted(meses), key="mes_recurso")

        datos_filtrados_mes = df[df["Mes"] == mes_seleccionado]

        actividades = datos_filtrados_mes["Actividad"].unique()
        actividades_seleccionadas = st.multiselect("Seleccione actividades", sorted(actividades), key="actividades_recurso")

        datos_recurso = datos_filtrados_mes
        if actividades_seleccionadas:
            datos_recurso = datos_recurso[datos_recurso["Actividad"].isin(actividades_seleccionadas)]

        ver_recursos = st.checkbox("Ver información de 'Recurso'")

        if ver_recursos:
            clave = st.text_input("Ingrese la clave para ver 'Recurso':", type="password")
            clave_correcta = "clave123"  # Cambia esto por la clave que desees

            if clave == clave_correcta:
                st.success("Acceso concedido. Información de 'Recurso' y datos asociados:")
                recursos_filtrados = datos_recurso[["Recurso", "Proyecto", "Actividad", "Descripción"]].drop_duplicates()
                
                # Aplicar colores intercalados con fondo alternado entre #9b2148 y #a87f2f
                html_content = """<style>
                                  table {width: 100%;}
                                  th, td {border: 1px solid #ddd; padding: 8px;}
                                  tr:nth-child(even) {background-color: #9b2148; color: white;}
                                  tr:nth-child(odd) {background-color: #a87f2f; color: white;}
                                  </style><table>"""
                # Agregar cabecera de la tabla
                html_content += "<tr><th>Recurso</th><th>Proyecto</th><th>Actividad</th><th>Descripción</th></tr>"
                for _, row in recursos_filtrados.iterrows():
                    html_content += f"<tr><td>{row['Recurso']}</td><td>{row['Proyecto']}</td><td>{row['Actividad']}</td><td>{row['Descripción']}</td></tr>"
                html_content += "</table>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.error("Clave incorrecta. No puede acceder a la información de 'Recurso'.")

    elif menu == "Editar CSV":
        # Funcionalidad para editar el CSV
        st.subheader("Edición del CSV")
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

        # Botón para guardar cambios
        if st.button("Guardar cambios"):
            edited_df.to_csv(CSV_PATH, index=False)
            st.success("Cambios guardados exitosamente en el archivo CSV.")



