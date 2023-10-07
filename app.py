import json
import re
from datetime import datetime
import pandas as pd
import streamlit as st
from sodapy import Socrata

# Title text and description
st.title(
    """
Explorador de Contratos SECOP
Distintas visualizaciones y análisis de los contratos públicos publicados en SECOP II

---
Agrega los filtros que desees y haz clic en **obtener datos**  
"""
)

# Set up filters
with open("data/metadata.json", "r") as f:
    metadata = json.load(f)

metadata_column_fieldname_dict = {}

for column in metadata["columns"]:
    # Extract the "fieldName" and "name" values
    fieldName = column["fieldName"]
    name = column["name"]

    # Add them to the result_dict
    metadata_column_fieldname_dict[name] = fieldName

with open("data/unique_values.json", "r") as f:
    unique_values = json.load(f)

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
            options=[column["name"] for column in metadata["columns"]],
            key=f"filter_{i+1}",
            index=None,
            placeholder="Selecciona una columna",
        )
    with filter_col2:
        if (
            st.session_state[f"filter_{i+1}"] != None
            and metadata_column_fieldname_dict[st.session_state[f"filter_{i+1}"]]
            in unique_values.keys()
        ):
            st.selectbox(
                label="Operador",
                options=[
                    o
                    for o in metadata["operators"].keys()
                    if metadata["operators"][o] not in ("<", ">", "<=", ">=")
                ],
                key=f"operator_filter_{i+1}",
                label_visibility="hidden",
            )
        else:
            st.selectbox(
                label="Operador",
                options=metadata["operators"].keys(),
                key=f"operator_filter_{i+1}",
                label_visibility="hidden",
            )
    with filter_col3:
        if (
            st.session_state[f"filter_{i+1}"] != None
            and metadata_column_fieldname_dict[st.session_state[f"filter_{i+1}"]]
            in unique_values.keys()
            and metadata["operators"][st.session_state[f"operator_filter_{i+1}"]]
            in [
                "=",
                "<>",
            ]
        ):
            st.selectbox(
                label="Selecciona un valor",
                options=unique_values[
                    metadata_column_fieldname_dict[st.session_state[f"filter_{i+1}"]]
                ],
                key=f"value_filter_{i+1}",
                label_visibility="hidden",
            )
        else:
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
if "filter_logic" not in st.session_state:
    st.session_state.filter_logic = "Todos cumplen (AND)"

if "logic_string" not in st.session_state:
    st.session_state.logic_string = ""


def change_filter_logic():
    st.session_state.filter_logic = st.session_state.radio_filter_logic


st.radio(
    label="Escoge la lógica entre tus filtros:",
    options=["Todos cumplen (AND)", "Cualquiera cumple (OR)", "Lógica personalizada"],
    horizontal=True,
    key="radio_filter_logic",
    on_change=change_filter_logic,
    index=0,
)


if st.session_state.filter_logic == "Lógica personalizada":
    st.markdown(
        """
    <small> Define la lógica entre tus filtros utilizando las palabras AND, OR, NOT, y paréntesis.
    Haz refencia a cada filtro con su numeración
    
    Ejemplo: *1 AND 2 OR (3 AND NOT 4)*</small>""",
        unsafe_allow_html=True,
    )
    st.session_state.logic_string = st.text_input(
        label="Lógica personalizada",
        label_visibility="collapsed",
        key="logic_string_input",
    )


def build_query():
    # Set up filter string
    if st.session_state.filter_logic == "Lógica personalizada":
        where_clause = st.session_state.logic_string.upper()
        for i in range(st.session_state.num_filters):
            where_clause = where_clause.replace(str(i + 1), f"[FILTER_{i+1}]")
    else:
        where_clause = ""

    filter_list = [
        [
            column["fieldName"]
            for column in metadata["columns"]
            if column["name"] == st.session_state[f"filter_{x+1}"]
        ][0]
        for x in range(st.session_state.num_filters)
    ]
    data_type_list = [
        [
            column["dataTypeName"]
            for column in metadata["columns"]
            if column["name"] == st.session_state[f"filter_{x+1}"]
        ][0]
        for x in range(st.session_state.num_filters)
    ]  # calendar_date, number, text, url
    operators_list = [
        metadata["operators"][st.session_state[f"operator_filter_{x+1}"]]
        for x in range(st.session_state.num_filters)
    ]
    values_list = [
        st.session_state[f"value_filter_{x+1}"]
        for x in range(st.session_state.num_filters)
    ]

    for i in range(st.session_state.num_filters):
        filter_string = ""
        filter_formatted = filter_list[i]

        if data_type_list[i] != "number":
            if operators_list[i] == "like" and data_type_list[i] == "text":
                value_formatted = "'%" + values_list[i].lower() + "%'"
                filter_formatted = f"lower({filter_formatted})"
            else:
                value_formatted = "'" + values_list[i] + "'"
        else:
            value_formatted = values_list[i]

        filter_string += (
            filter_formatted + " " + operators_list[i] + " " + value_formatted
        )

        if st.session_state.filter_logic != "Lógica personalizada":
            if i < st.session_state.num_filters - 1:
                if st.session_state.filter_logic == "Todos cumplen (AND)":
                    filter_string += " AND "
                elif st.session_state.filter_logic == "Cualquiera cumple (OR)":
                    filter_string += " OR "
            where_clause += filter_string
        else:
            where_clause = where_clause.replace(f"[FILTER_{i+1}]", filter_string)

    return where_clause


if "contract_dataframe" not in st.session_state:
    st.session_state.contract_dataframe = None


def get_data():
    where_clause = build_query()

    # set up socrata client
    client = Socrata("www.datos.gov.co", None)

    results = client.get(
        "jbjy-vk9h", where=where_clause, limit=1000, content_type="json"
    )
    results_df = pd.DataFrame.from_records(
        results,
    )
    st.session_state.contract_dataframe = results_df


st.divider()

st.button("Obtener datos", on_click=get_data, key="get_data_button")

if st.session_state.get_data_button:
    st.dataframe(st.session_state.contract_dataframe)
