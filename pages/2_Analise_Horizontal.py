import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px

st.set_page_config(layout='wide', page_title='Agrupamento')

df = st.session_state["data"]

st.markdown("<h1 style='color: #FFA500;'>Tabela agrupada</h1>", unsafe_allow_html=True)

st.markdown("Base de dados para análise horizontal por agrupamento")

st.sidebar.markdown("### Filtros")

filtrar_por_mes = st.sidebar.checkbox('Filtrar por período')


agrupar_ = st.sidebar.checkbox('Agrupar')


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

    # Aplicar filtro:
df_filtrado = df.copy()

if filtrar_por_mes:
    df_filtrado = df_filtrado[df_filtrado['Mês/Ano'].between(mes_inicial, mes_final)]

if agrupar_:
    df_filtrado = df_filtrado.groupby(['Conta', 'Descrição', 'Mês/Ano','Fornecedor', 'Centro de Custo'])['Valor'].sum().reset_index()

    # Criar pivot table
    df_filtrado_pivot = df_filtrado.pivot_table(
        index=['Conta', 'Descrição', 'Fornecedor', 'Centro de Custo'],
        columns='Mês/Ano',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )
    df_filtrado_pivot['Total'] = df_filtrado_pivot.sum(axis=1)
    df_filtrado_pivot = df_filtrado_pivot.sort_values('Total', ascending=False)

    # adicionar filtros de conta, fornecedor e centro de custo
    contas_disponiveis = sorted(df_filtrado['Conta'].unique())

    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        conta_selecionada = st.selectbox('Selecione a conta:', contas_disponiveis)
    
    # Filtrar fornecedores baseados na conta selecionada
    fornecedores_disponiveis = sorted(df_filtrado[df_filtrado['Conta'] == conta_selecionada]['Fornecedor'].unique())

    with col2:
        fornecedor_selecionado = st.selectbox('Selecione o fornecedor:', ['Todos'] + fornecedores_disponiveis)
    
    # Filtrar centros de custo baseados na conta e fornecedor selecionados
    centros_custo_df = df_filtrado[df_filtrado['Conta'] == conta_selecionada]
    if fornecedor_selecionado != 'Todos':
        centros_custo_df = centros_custo_df[centros_custo_df['Fornecedor'] == fornecedor_selecionado]
    
    centros_custo_disponiveis = sorted(centros_custo_df['Centro de Custo'].unique())

    with col3:
        centro_custo_selecionado = st.selectbox('Selecione o centro de custo:', ['Todos'] + centros_custo_disponiveis)

   # Aplicar os filtros selecionados ao df_filtrado_pivot
    df_filtrado_pivot_final = df_filtrado_pivot
    if conta_selecionada:
        df_filtrado_pivot_final = df_filtrado_pivot_final.loc[df_filtrado_pivot_final.index.get_level_values('Conta') == conta_selecionada]
    if fornecedor_selecionado != 'Todos':
        df_filtrado_pivot_final = df_filtrado_pivot_final.loc[df_filtrado_pivot_final.index.get_level_values('Fornecedor') == fornecedor_selecionado]
    if centro_custo_selecionado != 'Todos':
        df_filtrado_pivot_final = df_filtrado_pivot_final.loc[df_filtrado_pivot_final.index.get_level_values('Centro de Custo') == centro_custo_selecionado]

    # Calcular a altura da tabela
    num_rows = len(df_filtrado_pivot_final)
    table_height = max(400, min(600, num_rows * 35))  # Ajuste o multiplicador conforme necessário
else:
    # Criação da pivot table original (não agrupada)
    df_filtrado_pivot = df_filtrado.pivot_table(
        index=['Conta', 'Descrição', 'Fornecedor', 'Centro de Custo'],
        columns='Mês/Ano',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )
    df_filtrado_pivot['Total'] = df_filtrado_pivot.sum(axis=1)
    df_filtrado_pivot = df_filtrado_pivot.sort_values('Total', ascending=False)

    # calcular a altura da tabela
    num_rows = len(df_filtrado_pivot)
    table_height = max(400, min(600, num_rows * 35))  # Ajuste o multiplicador conforme necessário

st.dataframe(df_filtrado_pivot_final if agrupar_ else df_filtrado_pivot, height=table_height, width=1800)

st.markdown("### Gráfico da Movimentação por período")

# Colunas para o gráfico
col1, col2 = st.columns([1, 6])

# Seleção do tipo de gráfico
with col1:
    chart_type = st.selectbox("Tipo de Gráfico", ["Barras", "Pontos com Linhas"])

# Preparar os dados para o gráfico
if agrupar_:
    df_grafico = df_filtrado_pivot_final.reset_index()
else:
    df_grafico = df_filtrado_pivot.reset_index()

# Melt o dataframe para ter uma coluna de 'Mês/Ano' e uma coluna de 'Valor'
df_grafico_melted = pd.melt(df_grafico, 
                            id_vars=['Conta', 'Descrição', 'Fornecedor', 'Centro de Custo'], 
                            var_name='Mês/Ano', 
                            value_name='Valor')

# Remover a coluna 'Total' se existir
df_grafico_melted = df_grafico_melted[df_grafico_melted['Mês/Ano'] != 'Total']

# Agrupar os dados por Mês/Ano e somar os valores
df_agrupado = df_grafico_melted.groupby('Mês/Ano')['Valor'].sum().reset_index()

# Ordenar o dataframe por Mês/Ano
df_agrupado = df_agrupado.sort_values('Mês/Ano')

# Criar o gráfico baseado no tipo selecionado
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