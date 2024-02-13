#======================================
#Lobraries
#======================================

import streamlit as st
from PIL import Image

#======================================
# Funções
#======================================

st.set_page_config(
    page_title="home", 
    page_icon="🎲"
    )


#image_path = 'C:/Users/edjun/Documents/DS/repos/portifolio_projetos/img/pablo-mX0987sQP8E-unsplash.jpg' # SITE: unsplash
image = Image.open('pablo-mX0987sQP8E-unsplash.jpg')
st.sidebar.image(image, width=250)

st.sidebar.markdown('# Curry Company') 
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('Curry Company Growth Dashboard')

st.markdown(
    """ Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa
        - Visão Gerencia: métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador: 
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante: 
        - Acompanhamento dos indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
        - Time Data Science no Discord
        - @Edson
    """)