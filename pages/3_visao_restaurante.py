#======================================
#Lobraries
#======================================


#pip install haversine
#pip install plotly_express
#pip install folium

import numpy as np
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

st.set_page_config(page_title="Visão Restaurante", page_icon="🥩", layout="wide")

#======================================
# Funções
#======================================

def avg_std_time_on_traffic (df1):
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)' : ['mean', 'std']}))
    
    df_aux.columns = ['avg_Time', 'std_Time']
    df_aux = df_aux.reset_index()
    
    fig = (px.sunburst(df_aux, path=['City', 'Road_traffic_density']
                       , values='avg_Time'
                       , color='std_Time'
                       , color_continuous_scale='RdBu'
                       , color_continuous_midpoint=np.average(df_aux['std_Time'])))
    return fig



def avg_std_time_graph(df1):

    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ['avg_Time', 'std_Time']
    df_aux = df_aux.reset_index()
            
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], 
                                         y=df_aux['avg_Time'], 
                                         error_y=dict(type='data', array=df_aux['std_Time'])))
            
    fig.update_layout(barmode='group')

    return fig


def avg_std_time_delivery (df1, festival, op):

    """ 
        Está função calcula o tempo médio e desvio padrão do tempo de entrega.
        Parâmetros: 
            Input
                - df: dataframe com os dados necessários para cálculos 
                - op: tipo de operação que precisa ser cálculado
                    'avg_time': cálculo do tempo médio
                    'std_time': cálculo do desvio padrão do tempo
            Output
                - df: dataframe com 2 colunas e 1 linha.
    """

    df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                  .groupby(['Festival'])
                  .agg({'Time_taken(min)': ['mean', 'std']}))
    
    df_aux.columns = ['avg_Time_taken(min)', 'std_Time_taken(min)']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op] ,2)
        
    return df_aux

def distance(df1, fig):
    if fig == False:
        col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['Distance'] = df1.loc[:, col].apply(lambda x:
                               haversine(
                                   (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['Distance'].mean(),2)

        return avg_distance

    else:
        col = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['Distance'] = df1.loc[:, col].apply(lambda x:
                               haversine(
                                   (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()        
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['Distance'],pull=[0, 0.1, 0])])

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
# VISÃO RESTAURANTE
#======================================


# Quantidade de pedidos por dia
df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
df_aux.columns = ['order_date', 'qtde_entregas']
# gráfico
px.bar( df_aux, x='order_date', y='qtde_entregas' )

#======================================
# Barra lateral (sidebar)
#======================================
st.header('Marketplace - Visão Restaurantes')

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
        st.title('Overal Metrics')

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        
        delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
        col1.metric('Entregadores', delivery_unique)
        
    with col2:
        avg_distance = distance(df1, fig=False)
        col2.metric('A distancia média é', avg_distance)

    with col3:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_Time_taken(min)')
        col3.metric('Tempo médio', df_aux)
              
    with col4:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'std_Time_taken(min)')
        col4.metric('STD Entrega', df_aux)

        
    with col5:
        df_aux = avg_std_time_delivery(df1, 'No', 'avg_Time_taken(min)')
        col5.metric('Festival - Tempo médio', df_aux)      
        
    with col6:
        df_aux = avg_std_time_delivery(df1, 'No', 'std_Time_taken(min)')
        col6.metric('Festival - Std', df_aux)
        
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Tempo Médio de entregas por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:

            st.markdown('##### Distribuição da distancia')
            
            df_aux = (df1.loc[:, ['City', 'Type_of_order','Time_taken(min)']]
                      .groupby(['City', 'Type_of_order'])
                      .agg ({'Time_taken(min)' : ['mean', 'std']}))
            
            df_aux.columns = ['avg_Time_taken(min)', 'std_Time_taken(min)']
            df_aux.reset_index().sort_values(['Type_of_order', 'avg_Time_taken(min)'], ascending=False)
            st.dataframe(df_aux, use_container_width=True)
    
    
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)

        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = avg_std_time_on_traffic (df1)
            st.plotly_chart(fig, use_container_width=True)

    