import streamlit as st
import os
from snowflake.snowpark.functions import col
from cryptography.hazmat.primitives import serialization

# Write directly to the app
st.title(f" :cup_with_straw: Customize Your Smoothie!:cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom smoothie
  """)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)


key_cfg = st.secrets["snowflake_key"]
p_key = serialization.load_pem_private_key(
    key_cfg["pem"].encode(),
    password=key_cfg["passphrase"].encode(),
)
pkb = p_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

cnx = st.connection("snowflake", private_key=pkb)
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    )


if ingredients_list:
    ingredients_string = ''
    editable_df = st.data_editor(my_dataframe)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """' , '""" + name_on_order + """')"""


    time_to_insert = st.button('Submit Order')

    #st.write(my_insert_stmt)
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

import requests

for fruit_chosen in ingredients_list:
    st.subheader(fruit_chosen + ' Nutrition Information')
    url = "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen.lower()
    smoothiefroot_response = requests.get(url)
    if smoothiefroot_response.status_code == 200:
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    else:
        st.warning(f"{fruit_chosen} information is not available from our nutrition provider.")

