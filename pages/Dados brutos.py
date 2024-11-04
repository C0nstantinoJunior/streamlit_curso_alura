import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data #manter a variável na memória. pq se for baixa ro mesmo arquivo já esta na memória

def converte_csv (df):
    return df.to_csv(index = False).encode('utf-8')

def msg_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(5)
    sucesso.empty()



st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns) ) # nome, opições, opições selecionadas inicialmente

st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione Produtos', dados['Produto'].unique(), dados['Produto'].unique())

with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0,5000)) # assim posso selecionar intervalo, diferente do filtro do ano que deve selecionar apenas um

with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))

query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''

# @ é para chamar uma variável criada, Produtos, Preço e Data de Compra, este ultimo está em `` pq o nome da coluna tem espaços

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}]  linhas e :blue[{dados_filtrados.shape[1]}] colunas')
st.dataframe(dados_filtrados)

st.markdown('Escreva o nome do arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    #collapsed é para não deixar espaço nenhum, pois apesar de está '' o sistema deixa um espaço em branco
    # valor padrão vai ser dados
    nome_arquivo += '.csv'

with coluna2:
    st.download_button("Fazer o downland da tabela em csv",
                       data = converte_csv(dados_filtrados),
                       file_name=nome_arquivo,
                       #mine = "text/csv",
                       on_click = msg_sucesso)
