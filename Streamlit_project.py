import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard Rango Serpa",
    initial_sidebar_state="expanded"
)

# Função para padronizar culinárias
def padronizar_culinarias(df):
    """
    Padroniza os nomes das culinárias para melhor análise:
    1. Padroniza nomes (ex: sempre usar "Italian" como base)
    2. Separa estilos múltiplos e conta individualmente
    3. Agrupa por culinária principal
    """
    
    # Dicionário de padronização de nomes
    padronizacao = {
        # Culinárias italianas
        'Italian': 'Italian',
        'Pizza': 'Italian',
        'Pasta': 'Italian',
        'Mediterranean': 'Italian',
        
        # Culinárias asiáticas
        'Chinese': 'Chinese',
        'Japanese': 'Japanese',
        'Thai': 'Thai',
        'Korean': 'Korean',
        'Vietnamese': 'Vietnamese',
        'Asian': 'Asian',
        
        # Culinárias indianas
        'Indian': 'Indian',
        'North Indian': 'Indian',
        'South Indian': 'Indian',
        'Mughlai': 'Indian',
        'Hyderabadi': 'Indian',
        
        # Culinárias americanas
        'American': 'American',
        'Mexican': 'Mexican',
        'BBQ': 'American',
        'Burgers': 'American',
        'Steakhouse': 'American',
        
        # Culinárias europeias
        'French': 'French',
        'German': 'German',
        'Spanish': 'Spanish',
        'Greek': 'Greek',
        'Turkish': 'Turkish',
        
        # Fast Food e outras
        'Fast Food': 'Fast Food',
        'Street Food': 'Street Food',
        'Cafe': 'Cafe',
        'Bakery': 'Bakery',
        'Desserts': 'Desserts',
        'Ice Cream': 'Desserts',
        
        # Culinárias específicas
        'Seafood': 'Seafood',
        'Vegetarian': 'Vegetarian',
        'Vegan': 'Vegetarian',
        'Halal': 'Halal',
        'Kosher': 'Kosher'
    }
    
    # Criar cópia do dataframe
    df_padronizado = df.copy()
    
    # Lista para armazenar todas as culinárias individuais
    todas_culinarias = []
    
    # Processar cada linha
    for idx, row in df_padronizado.iterrows():
        cuisines_str = str(row['Cuisines'])
        
        # Pular valores nulos ou vazios
        if pd.isna(cuisines_str) or cuisines_str in ['nan', 'NaN', 'None', '', 'Não especificado']:
            todas_culinarias.append(['Não especificado'])
            continue
        
        # Separar culinárias múltiplas (separadas por vírgula)
        cuisines_list = [c.strip() for c in cuisines_str.split(',')]
        
        # Padronizar cada culinária individual
        cuisines_padronizadas = []
        for cuisine in cuisines_list:
            cuisine = cuisine.strip()
            if cuisine:
                # Aplicar padronização se existir no dicionário
                if cuisine in padronizacao:
                    cuisines_padronizadas.append(padronizacao[cuisine])
                else:
                    # Se não estiver no dicionário, manter o nome original
                    cuisines_padronizadas.append(cuisine)
        
        todas_culinarias.append(cuisines_padronizadas)
    
    # Adicionar colunas com culinárias padronizadas
    df_padronizado['Cuisines_Padronizadas'] = todas_culinarias
    df_padronizado['Cuisine_Principal'] = [cuisines[0] if cuisines else 'Não especificado' for cuisines in todas_culinarias]
    df_padronizado['Total_Cuisines'] = [len(cuisines) for cuisines in todas_culinarias]
    
    return df_padronizado

# Função para carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv('dataset_atualizado.csv')
    # Converter colunas numéricas
    df['Aggregate rating'] = pd.to_numeric(df['Aggregate rating'], errors='coerce')
    df['Price range'] = pd.to_numeric(df['Price range'], errors='coerce')
    df['Average Cost for two'] = pd.to_numeric(df['Average Cost for two'], errors='coerce')
    df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')
    
    # CORREÇÃO CRÍTICA: Limpar dados da coluna Cuisines
    # Remover valores NaN e converter tudo para string
    df['Cuisines'] = df['Cuisines'].fillna('Não especificado').astype(str)
    # Remover valores vazios ou apenas espaços
    df['Cuisines'] = df['Cuisines'].replace(['', 'nan', 'NaN', 'None'], 'Não especificado')
    # Remover espaços em branco no início e fim
    df['Cuisines'] = df['Cuisines'].str.strip()
    
    # CORREÇÃO AUTOMÁTICA DOS NOMES DAS CIDADES
    df['City'] = df['City'].fillna('').astype(str)
    
    # Corrigir nomes de cidades corrompidas
    city_corrections = {
        'Brasí_lia': 'Brasília',
        'Sí£o Paulo': 'São Paulo',
        'Sí£o paulo': 'São Paulo',
        'Sí£o paulo': 'São Paulo',
        'Brasí_lia': 'Brasília',
        'Brasí_lia': 'Brasília'
    }
    
    # Aplicar correções
    for wrong_name, correct_name in city_corrections.items():
        df.loc[df['City'] == wrong_name, 'City'] = correct_name
    
    # Limpar dados da coluna City (remover valores nulos)
    df = df.dropna(subset=['City'])
    
    # APLICAR PADRONIZAÇÃO DE CULINÁRIAS
    df = padronizar_culinarias(df)
    
    return df

# Carregar dados
df = load_data()

# Sidebar com logo
st.sidebar.image('img/img1.png', width=200)

# Navegação entre páginas
page = st.sidebar.selectbox(
    "📱 Navegação",
    ["Página Principal", "Países", "Cidades"]
)

# PÁGINA PRINCIPAL
if page == "Página Principal":
    st.title("🍕 O Melhor lugar para encontrar seu mais novo restaurante favorito!")
    
    # Filtros no sidebar
    st.sidebar.header("🔍 Filtros")

    # Se o botão de limpar tiver sido clicado, aplicar valores padrão ANTES de instanciar widgets
    if st.session_state.get("do_reset_filters", False):
        st.session_state["f_country"] = "Todos"
        st.session_state["f_city"] = "Todos"
        st.session_state["f_cuisine"] = "Todas"
        st.session_state["f_min_rating"] = 0.0
        st.session_state["f_price"] = "Todos"
        st.session_state["do_reset_filters"] = False
    
    # Filtro por país
    countries = ['Todos'] + sorted(df['Country'].unique().tolist())
    selected_country = st.sidebar.selectbox("🌍 País", countries, key="f_country")
    
    # Filtro por cidade (dependente do país)
    if selected_country == 'Todos':
        cities = ['Todos'] + sorted(df['City'].unique().tolist())
    else:
        country_df = df[df['Country'] == selected_country]
        cities = ['Todos'] + sorted(country_df['City'].unique().tolist())
    selected_city = st.sidebar.selectbox("🏙️ Cidade", cities, key="f_city")
    
    # Filtro por culinária (usando culinárias padronizadas)
    cuisines_principais = ['Todas'] + sorted(df['Cuisine_Principal'].unique().tolist())
    selected_cuisine = st.sidebar.selectbox("🍽️ Culinária Principal", cuisines_principais, key="f_cuisine")
    
    # Filtro por avaliação
    min_rating = st.sidebar.slider("⭐ Avaliação Mínima", 0.0, 5.0, 0.0, 0.1, key="f_min_rating")
    
    # Filtro por tipo de preço
    price_types = ['Todos'] + sorted(df['Price Type'].unique().tolist())
    selected_price_type = st.sidebar.selectbox("💰 Tipo de Preço", price_types, key="f_price")
    
    # Aplicar filtros
    filtered_df = df.copy()
    
    if selected_country != 'Todos':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    if selected_city != 'Todos':
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    
    if selected_cuisine != 'Todas':
        filtered_df = filtered_df[filtered_df['Cuisine_Principal'] == selected_cuisine]
    
    filtered_df = filtered_df[filtered_df['Aggregate rating'] >= min_rating]
    
    if selected_price_type != 'Todos':
        filtered_df = filtered_df[filtered_df['Price Type'] == selected_price_type]
    
    # Botão para limpar filtros
    # Botão para limpar filtros: apenas seta flag; a aplicação do reset ocorre antes dos widgets
    def _trigger_reset_filters():
        st.session_state["do_reset_filters"] = True

    st.sidebar.button("🔄 Limpar Filtros", on_click=_trigger_reset_filters)
    
    # Conteúdo principal
    st.subheader("📍 Restaurantes Encontrados")
    st.dataframe(
        filtered_df[['Restaurant Name', 'City', 'Cuisine_Principal', 'Cuisines', 'Aggregate rating', 'Price Type']],
        use_container_width=True
    )
    
    # Estatísticas da página principal
    st.markdown("---")
    st.subheader("📊 Estatísticas Gerais")
    
    # Métricas em colunas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🌍 Países",
            value=df['Country'].nunique(),
            help="Total de países disponíveis no dataset"
        )
    
    with col2:
        st.metric(
            label="🏙️ Cidades",
            value=df['City'].nunique(),
            help="Total de cidades disponíveis no dataset"
        )
    
    with col3:
        st.metric(
            label="🍽️ Restaurantes",
            value=len(df),
            help="Total de restaurantes no dataset"
        )
    
    with col4:
        st.metric(
            label="🍕 Culinárias Principais",
            value=df['Cuisine_Principal'].nunique(),
            help="Total de tipos de culinária principal disponíveis"
        )
    
    with col5:
        st.metric(
            label="⭐ Avaliação Média",
            value=f"{df['Aggregate rating'].mean():.2f}",
            help="Avaliação média geral de todos os restaurantes"
        )
    
    # Estatísticas dos filtros aplicados
    st.markdown("---")
    st.subheader("🎯 Estatísticas dos Filtros Aplicados")
    
    col6, col7, col8, col9 = st.columns(4)
    
    with col6:
        st.metric(
            label="🔍 Restaurantes Filtrados",
            value=len(filtered_df),
            help="Quantidade de restaurantes após aplicar os filtros"
        )
    
    with col7:
        st.metric(
            label="🏙️ Cidades Filtradas",
            value=filtered_df['City'].nunique(),
            help="Quantidade de cidades nos resultados filtrados"
        )
    
    with col8:
        st.metric(
            label="🍕 Culinárias Principais Filtradas",
            value=filtered_df['Cuisine_Principal'].nunique(),
            help="Quantidade de culinárias principais nos resultados filtrados"
        )
    
    with col9:
        st.metric(
            label="⭐ Avaliação Média Filtrada",
            value=f"{filtered_df['Aggregate rating'].mean():.2f}",
            help="Avaliação média dos restaurantes filtrados"
        )
    
    # Footer da página principal
    st.markdown("---")
    st.markdown("**Powered by Streamlit | Desenvolvido por Leonardo Serpa**")

# PAÍSES (mantido como estava, mas usando culinárias padronizadas)
elif page == "Países":
    st.title("🌍 Análise de Países")
    
    # Filtro por país (MÚLTIPLO) - igual ao da aba Cidades
    countries_paises = sorted(df['Country'].unique().tolist())
    selected_countries_paises = st.sidebar.multiselect(
        "🌍 Países (Selecione quantos quiser)",
        countries_paises,
        default=countries_paises[:3],  # Seleciona os 3 primeiros por padrão
        help="Clique para selecionar/deselecionar países. Você pode escolher quantos quiser!"
    )
    
    # Aplicar filtro de países
    if len(selected_countries_paises) > 0:
        df_filtered_paises = df[df['Country'].isin(selected_countries_paises)]
        countries_text_paises = ", ".join(selected_countries_paises)
        if len(selected_countries_paises) == 1:
            countries_text_paises = selected_countries_paises[0]
    else:
        df_filtered_paises = df.copy()
        countries_text_paises = "Todos os países"
    
    # Mostrar informações do filtro aplicado
    st.info(f"📍 **Países selecionados:** {countries_text_paises} | **Total de cidades:** {df_filtered_paises['City'].nunique()} | **Total de restaurantes:** {len(df_filtered_paises)}")
    
    # Gráficos organizados em grade 2x2
    st.subheader("📊 Análise Comparativa por País")
    
    # Primeira linha de gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 1: Quantidade de restaurantes por país
        country_restaurants = df_filtered_paises['Country'].value_counts()
        fig_restaurants = px.bar(
            x=country_restaurants.values,
            y=country_restaurants.index,
            orientation='h',
            title="🍽️ Quantidade de Restaurantes por País",
            color_discrete_sequence=['#2E86AB'],  # Azul profissional para restaurantes
            labels={'x': 'Quantidade de Restaurantes', 'y': 'País'}
        )
        fig_restaurants.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Quantidade de Restaurantes",
            yaxis_title="País",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_restaurants, width='stretch')
    
    with col2:
        # Gráfico 2: Média de preço para duas pessoas por país
        country_avg_cost = df_filtered_paises.groupby('Country')['Average Cost for two'].mean().sort_values(ascending=False)
        fig_avg_cost = px.bar(
            x=country_avg_cost.values,
            y=country_avg_cost.index,
            orientation='h',
            title="💰 Média de Preço para Duas Pessoas por País",
            color_discrete_sequence=['#C73E1D'],  # Vermelho escuro para preços
            labels={'x': 'Preço Médio', 'y': 'País'}
        )
        fig_avg_cost.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Preço Médio para Duas Pessoas",
            yaxis_title="País",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_avg_cost, width='stretch')
    
    # Segunda linha de gráficos
    col3, col4 = st.columns(2)
    
    with col3:
        # Gráfico 3: Quantidade de cidades por país
        country_cities = df_filtered_paises.groupby('Country')['City'].nunique().sort_values(ascending=False)
        fig_cities = px.bar(
            x=country_cities.values,
            y=country_cities.index,
            orientation='h',
            title="🏙️ Quantidade de Cidades por País",
            color_discrete_sequence=['#A23B72'],  # Roxo elegante para cidades
            labels={'x': 'Quantidade de Cidades', 'y': 'País'}
        )
        fig_cities.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Quantidade de Cidades",
            yaxis_title="País",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_cities, width='stretch')
    
    with col4:
        # Gráfico 4: Quantidade de avaliações por país
        country_votes = df_filtered_paises.groupby('Country')['Votes'].sum().sort_values(ascending=False)
        fig_votes = px.bar(
            x=country_votes.values,
            y=country_votes.index,
            orientation='h',
            title="⭐ Quantidade de Avaliações por País",
            color_discrete_sequence=['#F18F01'],  # Laranja vibrante para avaliações
            labels={'x': 'Total de Avaliações', 'y': 'País'}
        )
        fig_votes.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Total de Avaliações",
            yaxis_title="País",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_votes, width='stretch')
    
    # Footer da página países
    st.markdown("---")
    st.markdown("**Powered by Streamlit | Desenvolvido por Leonardo Serpa**")

# CIDADES (mantido como estava, mas usando culinárias padronizadas)
elif page == "Cidades":
    st.title("🏙️ Análise de Cidades")
    
    # Filtro por país (MÚLTIPLO)
    countries_cities = sorted(df['Country'].unique().tolist())
    selected_countries_cities = st.sidebar.multiselect(
        "🌍 Países (Selecione quantos quiser)",
        countries_cities,
        default=countries_cities[:3],  # Seleciona os 3 primeiros por padrão
        help="Clique para selecionar/deselecionar países. Você pode escolher quantos quiser!"
    )
    
    # Aplicar filtro de países
    if len(selected_countries_cities) > 0:
        df_filtered = df[df['Country'].isin(selected_countries_cities)]
        countries_text = ", ".join(selected_countries_cities)
        if len(selected_countries_cities) == 1:
            countries_text = selected_countries_cities[0]
    else:
        df_filtered = df.copy()
        countries_text = "Todos os países"
    
    # Limpar valores nulos da coluna City
    df_filtered = df_filtered.dropna(subset=['City'])
    
    # Mostrar informações do filtro aplicado
    st.info(f"📍 **Países selecionados:** {countries_text} | **Total de cidades:** {df_filtered['City'].nunique()} | **Total de restaurantes:** {len(df_filtered)}")
    
    # Gráfico 1: Culinárias principais mais populares (usando culinárias padronizadas)
    st.subheader("🍕 Culinárias Principais Mais Populares - Diversidade Gastronômica")
    cuisine_principal_counts = df_filtered['Cuisine_Principal'].value_counts().head(10)
    fig_cuisine_pie = px.pie(
        values=cuisine_principal_counts.values,
        names=cuisine_principal_counts.index,
        title="🍕 Top 10 Culinárias Principais Mais Populares",
        labels={'value': 'Quantidade de Restaurantes', 'name': 'Tipo de Culinária'}
    )
    st.plotly_chart(fig_cuisine_pie, width='stretch')
    
    # Gráficos organizados em grade 2x2
    st.subheader("🏆 Análise de Cidades e Diversidade Culinária")
    
    # Calcular dados para ambos os gráficos
    city_counts = df_filtered['City'].value_counts()
    
    # Calcular para cada cidade: quantidade de restaurantes e tipos de culinárias principais únicos
    city_diversity = df_filtered.groupby('City').agg({
        'Restaurant Name': 'count',  # Conta restaurantes
        'Cuisine_Principal': 'nunique'        # Conta tipos de culinárias principais únicos
    }).rename(columns={
        'Restaurant Name': 'Total_Restaurantes',
        'Cuisine_Principal': 'Tipos_Culinarias_Principais_Unicos'
    })
    
    # Ordenar por quantidade de restaurantes (critério principal)
    city_diversity = city_diversity.sort_values('Total_Restaurantes', ascending=False)
    
    # Primeira linha de gráficos
    col_cities, col_diversity = st.columns(2)
    
    with col_cities:
        # Gráfico 2: Ranking das cidades com mais restaurantes
        # Adaptar o número de cidades mostradas
        if len(city_counts) >= 15:
            max_cities = 15
            title_cities = "Top 15 Cidades"
        elif len(city_counts) >= 10:
            max_cities = 10
            title_cities = "Top 10 Cidades"
        elif len(city_counts) >= 5:
            max_cities = 5
            title_cities = "Top 5 Cidades"
        else:
            max_cities = len(city_counts)
            title_cities = f"Todas as {len(city_counts)} Cidades"
        
        city_counts_display = city_counts.head(max_cities)
        
        fig_cities_ranking = px.bar(
            x=city_counts_display.values,
            y=city_counts_display.index,
            orientation='h',
            title="🏆 Ranking das Cidades com Mais Restaurantes",
            color_discrete_sequence=['#4ECDC4']
        )
        fig_cities_ranking.update_layout(
            showlegend=False, 
            height=400,
            xaxis_title="Quantidade de Restaurantes",
            yaxis_title="Cidade",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_cities_ranking, width='stretch')
    
    with col_diversity:
        # Gráfico 3: Top cidades com mais restaurantes e tipos de culinárias principais distintos
        if len(city_diversity) > 0:
            # Adaptar o número de cidades mostradas
            if len(city_diversity) >= 10:
                top_diversity = city_diversity.head(10)
                title_diversity = "Top 10 Cidades"
            elif len(city_diversity) >= 7:
                top_diversity = city_diversity.head(7)
                title_diversity = "Top 7 Cidades"
            elif len(city_diversity) >= 5:
                top_diversity = city_diversity.head(5)
                title_diversity = "Top 5 Cidades"
            else:
                top_diversity = city_diversity
                title_diversity = f"Todas as {len(city_diversity)} Cidades"
            
            # Criar gráfico de barras com duas métricas
            fig_diversity = px.bar(
                 x=top_diversity.index,
                 y=top_diversity['Total_Restaurantes'],
                 title="🍕 Top Cidades com Mais Restaurantes e Diversidade Culinária",
                 color_discrete_sequence=['#FFD700'],  # Cor dourada para destacar
                 labels={'x': 'Cidade', 'y': 'Total de Restaurantes'}
             )
            
            # Adicionar anotações com a quantidade de tipos de culinárias principais
            for i, (city, row) in enumerate(top_diversity.iterrows()):
                fig_diversity.add_annotation(
                    x=city,
                    y=row['Total_Restaurantes'] + (row['Total_Restaurantes'] * 0.05),  # Posicionar acima da barra
                    text=f"🍕 {int(row['Tipos_Culinarias_Principais_Unicos'])} tipos",
                    showarrow=False,
                    font=dict(size=10, color='#FF6B6B'),
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='#FF6B6B',
                    borderwidth=1
                )
            
            fig_diversity.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Cidade",
                yaxis_title="Total de Restaurantes",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_diversity, width='stretch')
        else:
            st.info(f"Nenhuma cidade encontrada nos países selecionados")
    
    # Segunda linha de gráficos
    st.subheader("⭐ Análise de Qualidade por Cidade - Média de Avaliação")
    
    # Calcular média de avaliação por cidade
    city_ratings = df_filtered.groupby('City')['Aggregate rating'].mean()
    
    # Criar duas colunas para os gráficos
    col_above_4, col_below_4 = st.columns(2)
    
    with col_above_4:
        # Gráfico 4: Cidades com média acima de 4
        city_ratings_above_4 = city_ratings[city_ratings > 4.0].sort_values(ascending=False)
        
        if len(city_ratings_above_4) > 0:
            # Adaptar o número de cidades mostradas
            if len(city_ratings_above_4) >= 7:
                top_cities = city_ratings_above_4.head(7)
                title_top = "Top 7 Cidades com Média Acima de 4"
            elif len(city_ratings_above_4) >= 5:
                top_cities = city_ratings_above_4.head(5)
                title_top = "Top 5 Cidades com Média Acima de 4"
            elif len(city_ratings_above_4) >= 3:
                top_cities = city_ratings_above_4.head(3)
                title_top = "Top 3 Cidades com Média Acima de 4"
            else:
                top_cities = city_ratings_above_4
                title_top = f"Todas as {len(city_ratings_above_4)} Cidades com Média Acima de 4"
            
            fig_top_cities = px.bar(
                x=top_cities.values,
                y=top_cities.index,
                orientation='h',
                title="⭐ Cidades com Média Acima de 4",
                color_discrete_sequence=['#FF6B6B']
            )
            fig_top_cities.update_layout(
                showlegend=False, 
                height=400,
                xaxis_title="Avaliação Média",
                yaxis_title="Cidade",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_top_cities, width='stretch')
        else:
            st.info(f"Nenhuma cidade encontrada com média de avaliação acima de 4.0")
    
    with col_below_4:
        # Gráfico 5: Cidades com média abaixo de 4
        city_ratings_below_4 = city_ratings[city_ratings < 4.0].sort_values(ascending=True)
        
        if len(city_ratings_below_4) > 0:
            # Adaptar o número de cidades mostradas
            if len(city_ratings_below_4) >= 10:
                below_4_cities = city_ratings_below_4.head(10)
                title_below_4 = "Top 10 Cidades com Média Abaixo de 4"
            elif len(city_ratings_below_4) >= 7:
                below_4_cities = city_ratings_below_4.head(7)
                title_below_4 = "Top 7 Cidades com Média Abaixo de 4"
            elif len(city_ratings_below_4) >= 5:
                below_4_cities = city_ratings_below_4.head(5)
                title_below_4 = "Top 5 Cidades com Média Abaixo de 4"
            else:
                below_4_cities = city_ratings_below_4
                title_below_4 = f"Todas as {len(city_ratings_below_4)} Cidades com Média Abaixo de 4"
            
            fig_below_4_cities = px.bar(
                x=below_4_cities.values,
                y=below_4_cities.index,
                orientation='h',
                title="⭐ Cidades com Média Abaixo de 4",
                color_discrete_sequence=['#FFA500']  # Cor laranja para diferenciar
            )
            fig_below_4_cities.update_layout(
                showlegend=False, 
                height=400,
                xaxis_title="Avaliação Média",
                yaxis_title="Cidade",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_below_4_cities, width='stretch')
        else:
            st.info(f"Nenhuma cidade encontrada com média de avaliação abaixo de 4.0")
    
    # Footer da página cidades
    st.markdown("---")

    st.markdown("**Criado com Streamlit por Leonardo Serpa**")
