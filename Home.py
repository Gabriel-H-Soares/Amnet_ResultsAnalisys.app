import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px

st.set_page_config(layout='wide', page_title='P&L-America Net')

if "data" not in st.session_state:
    df = pd.read_excel("datasets/Amnet_Base_P&L_2024.xlsx", sheet_name="Base_2024") 
    df = df[['CT2_DATA', 'Grupo', 'Sub-Grupo', 'Conta', 'Desc.conta', 'CT2_VALOR', 'CT2_CCD', 'A2_NOME']]
    df.columns = ['Data', 'Grupo', 'Sub-Grupo', 'Conta', 'Descrição', 'Valor', 'Centro de Custo', 'Fornecedor']
    df['Mês/Ano'] = df['Data'].dt.to_period('M').astype(str)
    df['Conta'] = df['Conta'].astype(str)
    df['Fornecedor'] = df['Fornecedor'].fillna('')
    df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y')
    st.session_state["data"] = df
        
df = st.session_state["data"]
    
st.markdown("<h1 style='color: #FFA500;'>Analise de Resultado da America Net</h1>", unsafe_allow_html=True)

st.markdown("Base de dados contêm a movimentação por conta, fornecedor e centro de custo de todo o resultado do período:")

st.sidebar.markdown("### Filtros")

filtrar_por_mes = st.sidebar.checkbox('Filtrar por período')

# Adicionar filtro de intervalo de meses
meses_disponiveis = sorted(df['Mês/Ano'].unique())
if filtrar_por_mes:
    st.sidebar.markdown("#### Filtrar por Mês")
    mes_inicial, mes_final = st.sidebar.select_slider(
        'Selecione o intervalo de meses',
        options=meses_disponiveis,
        value=(meses_disponiveis[0], meses_disponiveis[-1])
    )
else:
    mes_inicial, mes_final = meses_disponiveis[0], meses_disponiveis[-1]

filtrar_por_grupo = st.sidebar.checkbox('Filtrar por Grupo')
conta_filtro = st.sidebar.checkbox("Filtrar por Conta")
centro_custo_filtro = st.sidebar.checkbox("Filtrar por Centro de Custo")
fornecedor_filtro = st.sidebar.checkbox("Filtrar por Fornecedor")

# Aplicar filtros
df_filtrado = df

if filtrar_por_mes:
    df_filtrado = df_filtrado[df_filtrado['Mês/Ano'].between(mes_inicial, mes_final)]

if filtrar_por_grupo:
    grupo_selecionado = st.sidebar.selectbox('Selecione o Grupo', df['Grupo'].unique())
    df_filtrado = df_filtrado[df_filtrado['Grupo'] == grupo_selecionado]

if conta_filtro:
    conta_selecionada = st.sidebar.selectbox('Selecione a Conta', df['Conta'].unique())
    df_filtrado = df_filtrado[df_filtrado['Conta'] == conta_selecionada]

if centro_custo_filtro:
    centro_custo_selecionado = st.sidebar.selectbox('Selecione o Centro de Custo', df['Centro de Custo'].unique())
    df_filtrado = df_filtrado[df_filtrado['Centro de Custo'] == centro_custo_selecionado]

if fornecedor_filtro:
    fornecedor_selecionado = st.sidebar.selectbox('Selecione o Fornecedor', df['Fornecedor'].unique())
    df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_selecionado]
    
st.dataframe(df_filtrado, height=500, width=1500)

st.markdown("### Grafico da Movimentação por período")

# Colunas para o grafico

df_Graficos = df_filtrado.copy()

col1, col2 = st.columns([1, 6])

# Seleção do tipo de grafico
with col1:
    chart_type = st.selectbox("Tipo de Gráfico", ["Barras", "Pontos com Linhas"]) 

# Converter a coluna 'Data' para datetime
df_Graficos['Data'] = pd.to_datetime(df_Graficos['Data'], format='%d/%m/%Y')

# Agrupar os dados por Mês/Ano e somar os valores
df_agrupado = df_Graficos.groupby('Mês/Ano')['Valor'].sum().reset_index()

# Ordenar o dataframe por Mês/Ano
df_agrupado = df_agrupado.sort_values('Mês/Ano')

# Criar o grafico baseado no tipo selecionado
if chart_type == "Barras":
    fig = px.bar(df_agrupado, x='Mês/Ano', y='Valor', title='Movimentação por Período')
    fig.update_traces(
        marker_color='#FFA500',
        marker_line_color='#C71585',
        marker_line_width=1.5,
        opacity=0.8,
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )
    fig.update_layout(height=500)
else:
    fig = px.scatter(df_agrupado, x='Mês/Ano', y='Valor', title='Movimentação por Período')
    fig.add_trace(px.line(df_agrupado, x='Mês/Ano', y='Valor').data[0])
    fig.update_traces(
        marker=dict(size=10, color='#FFA500', symbol='circle'),
        line=dict(color='#C71585', width=2),
        mode='lines+markers+text',
        texttemplate='%{y:,.0f}',
        textposition='top center'
    )

fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Arial', size=12, color='black'),
    title=dict(font=dict(size=20, color='#333333')),
    xaxis=dict(
        title='Período',
        tickangle=45,
        tickfont=dict(size=10),
        gridcolor='lightgrey',
        showline=True,
        linewidth=1,
        linecolor='lightgrey'
    ),
    yaxis=dict(
        title='Valores Totais',
        tickformat=',.0f',
        gridcolor='lightgrey',
        showline=True,
        linewidth=1,
        linecolor='lightgrey'
    ),
    showlegend=False,
    width=600
)
# Exibir o gráfico
st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("Desenvolvido por **Gabriel Soares**")
