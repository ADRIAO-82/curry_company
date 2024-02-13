#======================================
#Lobraries
#======================================


#pip install haversine
#pip install plotly_express
#pip install folium

#import numpy as np
#import re
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
#from datetime import datetime
from PIL import Image
import datetime
from streamlit_folium import folium_static

st.set_page_config(page_title="Visão Entregadores", page_icon="🏍️", layout="wide")

#======================================
# Funções
#======================================

def top_delivery (df1, top_asc):
    df2 = (df1.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby(['City', 'Delivery_person_ID']).min()
               .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df3


def clean_code(df1):

    """ Está função tem a responsabilidade de limpar o dataframe
    Tipos de limprezas:
    1. Remoção dos NaN
    2. Mudança do tipo de dados nas colunas
    3. Remoção dos espaços das variáveis de texto
    4. Formatação da coluna data
    5. Limpeza da coluna de tempo (remoção de texto da variável numérica)

    Input: dataframe
    Output: dataframe
    
    """
    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    # Remover spaco da string
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # Convertendo multiple_deliveries de text para num int
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # limpando a coluna de Time_taken(min)
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1


#--------------------------------------------Inicio da estrutura do código--------------------------------------------------

#======================================
# Improt dataset
#======================================

df = pd.read_csv('dataset/train.csv')

#======================================
# limpar dataset/train.csv
#======================================
df1 = clean_code(df)


#======================================
# VISÃO ENTREGADORES
#======================================


# Quantidade de pedidos por dia
df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
df_aux.columns = ['order_date', 'qtde_entregas']
# gráfico
px.bar( df_aux, x='order_date', y='qtde_entregas' )

#======================================
# Barra lateral (sidebar)
#======================================
st.header('Marketplace - Visão Empresa')

#image_path = 'C:/Users/edjun/Documents/DS/repos/portifolio_projetos/img/pablo-mX0987sQP8E-unsplash.jpg' # SITE: unsplash
image = Image.open('pablo-mX0987sQP8E-unsplash.jpg')
st.sidebar.image(image, width=250)


st.sidebar.markdown('# Curry Company') 
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?', 
    value=datetime.datetime(2022, 4, 13), #data default se o usuário não escolher data
    min_value=datetime.datetime(2022, 2, 11),
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYY')

st.sidebar.markdown("""___""")

traffic_opitions = st.sidebar.multiselect(
	'Quais as condições do transito',
	['Low', 'Medium', 'High', 'Jam'],
	default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered By Comunidade DS')


#filter the datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filter the traffic
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_opitions)
df1 = df1.loc[linhas_selecionadas, :]

#======================================
# Layout Streamlit
#======================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.subheader('Maior de Idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade de', maior_idade)
            
        with col2:
            #st.subheader('Menor de Idade')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade de', menor_idade)
        
        with col3:
            #st.subheader('Melhor Condição de Veículo')
            melhor_vehicle_condition = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Veículo', melhor_vehicle_condition)

        with col4:
            #st.subheader('Pior Condição de Veículo')
            pior_vehicle_condition = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Veículo', pior_vehicle_condition)

    with st.container():
    	st.markdown("""___""")
    	st.title('Avaliações')

    	col1, col2, = st.columns(2)
    	with col1:
            st.markdown('##### Avaliação media por entregador')
            df_avg_delivery_person_ratings = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                              .groupby('Delivery_person_ID')
                                              .mean()
                                              .reset_index())
            st.dataframe(df_avg_delivery_person_ratings)
        
    	with col2:
            st.markdown('##### Avaliação media por Transito')
            df_avg_std_road_traffic_density = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                                               .groupby( 'Road_traffic_density' )
                                               .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
            df_avg_std_road_traffic_density.columns = ['Delivery_person_Ratings_mean', 'Delivery_person_Ratings_std']
            st.dataframe(df_avg_std_road_traffic_density.reset_index().sort_values('Delivery_person_Ratings_std', ascending=False))
        
        
        
            st.markdown('##### Avaliação media por Clima')
            df_avg_std_weatherconditions = (df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                                            .groupby( 'Weatherconditions' )
                                            .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
            df_avg_std_weatherconditions.columns = ['Delivery_person_Ratings_mean', 'Delivery_person_Ratings_std']
            st.dataframe(df_avg_std_weatherconditions.reset_index().sort_values('Delivery_person_Ratings_std', ascending=False))

    
    with st.container():
    	st.markdown("""___""")
    	st.title('Velocidade de Entrega')

    	col1, col2, = st.columns(2)
    	with col1:
            st.markdown('##### Top entregadores mais Rápidos')
            df3 = top_delivery (df1, top_asc=True)
            st.dataframe(df3)
            
    	with col2:
            st.markdown('##### Top entregadores mais Lentos')
            df3 = top_delivery (df1, top_asc=False)
            st.dataframe(df3)


            