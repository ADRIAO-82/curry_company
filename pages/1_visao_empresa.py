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

st.set_page_config(page_title="Visão Empresa", page_icon="🎯", layout="wide")

#======================================
# Funções
#======================================

def country_map(df1):
    """ Mapa."""
    df_aux = df1.loc[:,['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    # Desenhar o mapa
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)

    folium_static(map, width=1024, height=600)

def order_share_by_week (df1):
    """ A quantidade de pedidos por entregador por semana.
    Gráfico de Linha
    """
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig


def order_by_week (df1):
    """ A localização central de cada cidade por tipo de tráfego.
    Gráfico de Linha
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID')
    return fig


def traffic_order_city (df1):
    """ Comparação do volume de pedidos por cidade e tipo de tráfego.
    Gráfico de Scatter
    """
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .count()
                  .reset_index())
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig


def trafic_order_share(df1):
    """ Está função conta distribuição dos pedidos por tipo de tráfego.
    Gráfico de Pizza
    """
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby( 'Road_traffic_density' )
                  .count()
                  .reset_index())
    
    df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())
    # gráfico
    fig = px.pie(df_aux, values='perc_ID', names='Road_traffic_density')
    
    return fig

def order_metric(df1):
    """ Está função conta a quantidade de pedidos por dia
    Gráfico de barras
    """
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    # gráfico
    fig = px.bar(df_aux, x='order_date', y='qtde_entregas')
    return fig

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
# VISÃO EMPRESA
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        st.markdown('# Order by day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = trafic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city (df1)
            st.plotly_chart(fig, use_container_width=True)

                
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
     
    
    with st.container():
        st.markdown('# Order share by Week')
        fig = order_share_by_week (df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown(' # Country Maps')
    fig = country_map(df1)
