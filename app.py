import json
import pandas as pd
import streamlit as st
from sodapy import Socrata

# Title text and description
st.title(
    """
Explorador de Contratos SECOP
Distintas visualizaciones y análisis de los contratos públicos publicados en SECOP II

Agrega los filtros que desees y haz clic en **obtener datos**  
"""
)

# Set up filters
with open("data/filter_options.json", "r") as f:
    filter_options = json.load(f)

# Initialize the session state
if "num_filters" not in st.session_state:
    st.session_state.num_filters = 1

# Create a container to hold all the boxes
filter_container = st.container()
filter_col1, filter_col2, filter_col3 = filter_container.columns([1.1, 0.8, 1.1])
# Add boxes inside the container
for i in range(st.session_state.num_filters):
    with filter_col1:
        st.selectbox(
            label=f"Filtro {i+1}",
            options=filter_options["columns"].keys(),
            key=f"filter_{i+1}",
            index=None,
            placeholder="Selecciona una columna",
        )
    with filter_col2:
        st.selectbox(
            label="Operador",
            options=filter_options["operators"].keys(),
            key=f"operator_filter_{i+1}",
            label_visibility="hidden",
        )
    with filter_col3:
        st.text_input(
            label="Selecciona un valor",
            label_visibility="hidden",
            placeholder="Valor",
            key=f"value_filter_{i+1}",
        )

# Create placeholders for the buttons
button_col1, button_col2 = st.columns([0.207, 1])

# Add the 'Add Filter' button in the first column
add_filter = button_col1.button(label="Agregar filtro")

# If the 'Add Filter' button is clicked, increase the number of boxes and rerun the script
if add_filter:
    st.session_state.num_filters += 1
    st.rerun()

# Add the 'Remove Filter' button in the second column
if st.session_state.num_filters > 1:
    remove_filter = button_col2.button(
        label=":red[Remover filtro]",
    )
else:
    remove_filter = None

# If the 'Remove Filter' button is clicked, decrease the number of boxes and rerun the script
if remove_filter:
    if st.session_state.num_filters > 1:
        st.session_state.num_filters -= 1
    st.rerun()

# Add filter logic input
filter_logic_radio = st.radio(
    label="Escoge la lógica entre tus filtros:",
    options=["Todos cumplen (AND)", "Cualquiera cumple (OR)", "Lógica personalizada"],
    horizontal=True,
)
if filter_logic_radio == "Lógica personalizada":
    st.markdown(
        """
    <small> Define la lógica entre tus filtros utilizando las palabras AND, OR, NOT, y paréntesis.
    Haz refencia a cada filtro con su numeración

    Ejemplo: *1 AND 2 OR (3 AND NOT 4)*</small>""",
        unsafe_allow_html=True,
    )
    logic_string = st.text_input(
        label="Lógica personalizada", label_visibility="collapsed"
    )


# # set up socrata client
# client = Socrata("www.datos.gov.co", None)

# results = client.get(
#     "jbjy-vk9h",
#     where="nit_entidad=899999114 and lower(proveedor_adjudicado) like '%claudia andrea%'",
#     limit=1000,
#     content_type="json",
# )
# results_df = pd.DataFrame.from_records(
#     results,
# )
# results_df
