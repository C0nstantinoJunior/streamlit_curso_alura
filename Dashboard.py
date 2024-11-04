import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

st.title('DASHBOARD :shopping_trolley:')
st.sidebar.title('Filtros')

## Funções

def formatar_numero(valor, prefixo = ''):
    
    for vl_ref in [[1000, 1,""], [1000000, 1000, "mil"], [1000000000, 1000000, 'milhões']]:
        if valor < vl_ref[0]:
            valor = valor/vl_ref[1]
            unidade = vl_ref[2]
            return f' {prefixo} {valor:.2f} {unidade}'
    return f'{prefixo} {valor/1000000000:.2f} bilhões'
## Importar Dados

url = 'https://labdados.com/produtos'
### Filtros
regioes = ['Brasil', 'Norte', 'Nordeste', 'Centro-Oeste','Sudeste', 'Sul']
regiao = st.sidebar.selectbox('Região', regioes)
if regiao =='Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todos os anos', value=True)
if todos_anos:
    ano=''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

### Passa os filtros para url
query_string = {'regiao':regiao.lower(), 'ano': ano} # pq só aceita letra minúscula


### Tabela de dados
response = requests.get(url, params = query_string) # antes de passar os filtros response = requests.get(url), só baixa o arquivo
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

### Filtro direto na tabela

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores: #verifica se há um filtro
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


## Tabelas
### Tabelas de Receitas
receitas_estados = dados.groupby('Local da compra')[['Preço']].sum()
lat_lon_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']]
receitas_estados = lat_lon_estados.merge(receitas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas quantidade de vendas

### Tabelas Vendedores

vendedores = dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])

## Gráficos

fig_mapa_receita = px.scatter_geo(receitas_estados, 
                                  lat='lat',
                                  lon='lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon': False}, 
                                  title='Receita por Estados',
                                  )

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers= True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita Mensal')

fig_receita_estado = px.bar(receitas_estados.head(5),
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto=True,
                            title='Top Estados (Receita)')
fig_receita_estado.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                            text_auto=True,
                            title='Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')
   
        
## Visualização no streamlit

aba1, aba2,aba3,aba4 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendendores', 'Tabela'])

with aba1:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum()))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estado, use_container_width=True)

    with col2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)


with aba2:
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum()))

    with col2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]))
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2,10,5) # número mínimo, máximo e padrão
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita', formatar_numero(dados['Preço'].sum()))
        df = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores)
        fig_receita_vendedores = px.bar(df,
                                        x = 'sum',
                                        y = df.index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with col2:
        st.metric('Quantidade de Vendas', formatar_numero(dados.shape[0]))
        df = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores)
        fig_vendas_vendedores = px.bar(df,
                                        x = 'count',
                                        y = df.index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores)

with aba4:
    st.dataframe(dados)





