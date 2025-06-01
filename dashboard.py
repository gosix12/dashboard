import streamlit as st
import pandas as pd
import os
import gdown
import graphviz
import streamlit.components.v1 as components
from PIL import Image
import calendar
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="SmartPromocje, czyli jak dane pomagają przewidywać sprzedaż leków", layout="wide")

@st.cache_data(show_spinner=True)
def download_and_load_parquet(file_id: str, filename: str) -> pd.DataFrame:
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)
    return pd.read_parquet(filename)

rok_2022 = download_and_load_parquet("1dNNjD4_nAjEfdOCmXRW2IkJRWrmZOKv2", "rok_2022.parquet")
rok_2023 = download_and_load_parquet("12mhaL_5ii73QTuNBDLj-g_8m6hW4Pt62", "rok_2023.parquet")
rok_2024 = download_and_load_parquet("1sFG4A0j4qvBeGleAChgQPPc3nSkjfgNf", "rok_2024.parquet")

@st.cache_data
def load_excel(file_id: str, filename: str, engine='openpyxl') -> pd.DataFrame:
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)
    return pd.read_excel(filename, engine=engine)

rynek = load_excel("1-ht0X_NyVlJI8hOxxzKp6Z-4c7uvR-z7", "rynek.xlsx")
# Zakładki
tab00,tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏢 O firmie", 
    "📂 Charakterystyka danych", 
    "📊 Struktura danych",
    "📈 Wykresy czasowe",
    "🏆 Top 5",
    "🧮 Analiza Pareto",
    "🧩 Udziały rynkowe",
    "📉 Statystyki najlepszego i najgorszego modelu"
])
# --- Funkcje pomocnicze ---
def info_card(title, value, color, icon):
        st.markdown(f"""
        <div style='padding: 15px; background-color: {color}; border-radius: 12px; text-align: center; color: white;'>
            <div style='font-size: 22px;'>{icon}</div>
            <div style='font-size: 16px; font-weight: bold;'>{title}</div>
            <div style='font-size: 20px;'>{value}</div>
        </div>
        """, unsafe_allow_html=True)
dane_lata = {
        2022: rok_2022,
        2023: rok_2023,
        2024: rok_2024
}
with tab00:
    # ID
    file_id_neuca = "1PieF2gv5iiInKE-8s2h5D_918x3kRGyJ"
    def download_if_not_exists(file_id, filename):
        if not os.path.exists(filename):
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, filename, quiet=False)

    download_if_not_exists(file_id_neuca, "neuca_logo.png")
    logo = Image.open("neuca_logo.png")
    st.image(logo, width=300)

    html_code = """
    <style>
    .custom-tab .section {
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: 25px;
        margin-bottom: 30px;
        color: #111111;
        font-size: 20px;
        line-height: 1.6;
    }

    .custom-tab .timeline {
        border-left: 5px solid #1f77b4;
        padding-left: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
        color: #111111;
    }

    .custom-tab .timeline-event {
        margin-bottom: 20px;
        font-size: 20px;
        color: #111111;
        font-weight: 600;
        line-height: 1.5;
    }

    .custom-tab .timeline-event strong {
        color: #1f77b4;
        font-weight: 800;
        font-size: 20px;
        margin-right: 15px;
    }

    .custom-tab h1, .custom-tab h2, .custom-tab h3 {
        font-size: 28px;
        color: #0d47a1;
        margin-bottom: 15px;
    }

    .custom-tab ul {
        font-size: 20px;
        line-height: 1.6;
        color: #111111;
    }

    .custom-tab p {
        color: #111111;
    }
    </style>

    <div class="custom-tab">
        <div class="section">
            <h1>🏢 O firmie NEUCA</h1>
            <p><strong>NEUCA S.A.</strong> to wiodąca firma z sektora ochrony zdrowia, która od ponad 30 lat aktywnie kształtuje polski rynek farmaceutyczny. Jej korzenie sięgają <strong>1990 roku</strong>, kiedy to w Toruniu powstała hurtownia leków TORFARM.</p>
            <p>Z małej, lokalnej inicjatywy NEUCA przekształciła się w jednego z kluczowych graczy w kraju. Dziś to <strong>strategiczny partner dla tysięcy aptek</strong>, placówek medycznych i firm z branży zdrowotnej.</p>
        </div>

        <div class="section">
            <h3>🕰 Kluczowe daty z historii firmy:</h3>
            <div class="timeline">
                <div class="timeline-event"><strong>1990</strong>– Kazimierz Herba zakłada hurtownię leków TORFARM w Toruniu</div>
                <div class="timeline-event"><strong>2001</strong>– firma obejmuje zasięgiem 90% powierzchni kraju</div>
                <div class="timeline-event"><strong>2007</strong>– powstaje Grupa TORFARM</div>
                <div class="timeline-event"><strong>2010</strong>– powstaje Grupa NEUCA, a TORFARM staje się jej częścią</div>
                <div class="timeline-event"><strong>2013</strong>– powstaje NEUCA Med, rozwijająca sieć przychodni</div>
                <div class="timeline-event"><strong>2018</strong>– uruchomienie centrum dystrybucyjnego przy ul. Fortecznej</div>
                <div class="timeline-event"><strong>2020</strong>– otwarcie nowej centrali firmy w Toruniu</div>
            </div>
        </div>

        <div class="section">
            <h3>🔍 Czym się zajmujemy?</h3>
            <ul>
                <li>💊 <strong>Dystrybucja leków</strong> – kompleksowe zaopatrzenie aptek i logistyka.</li>
                <li>🤝 <strong>Współpraca z aptekarzami</strong> – narzędzia, doradztwo, niezależność.</li>
                <li>🏥 <strong>Rozwój przychodni</strong> – NEUCA Med i Świat Zdrowia.</li>
                <li>🧪 <strong>Badania kliniczne</strong> – innowacyjne terapie i R&D.</li>
                <li>📡 <strong>Telemedycyna</strong> – zdalna opieka medyczna.</li>
                <li>🛒 <strong>E-commerce</strong> – cyfrowe platformy sprzedaży i wsparcia.</li>
            </ul>
        </div>

        <div class="section">
            <h3>🧭 Nasza misja</h3>
            <p>Celem NEUCA jest <strong>budowanie lepszego systemu opieki zdrowotnej</strong> w Polsce poprzez integrację logistyki, medycyny i technologii – w oparciu o zaufanie, jakość i innowację.</p>
        </div>
    </div>
    """

    components.html(html_code, height=1500, scrolling=True)


with tab0:
    st.markdown("""
    <style>
    .char-header {
        background-color: #000000;
        color: #ffffff;
        padding: 40px 30px;
        text-align: center;
        border-radius: 15px;
        margin-bottom: 30px;
    }

    .char-header h2 {
        font-size: 32px;
        margin-bottom: 20px;
        color: #ffffff;
    }

    .char-header p {
        font-size: 20px;
        color: #ffffff;
        margin: 0 auto;
        max-width: 850px;
    }

    .char-section {
        background-color: #ffffff;
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        color: #111111;
        font-size: 20px;
        line-height: 1.6;
    }

    .char-section h3 {
        color: #0d47a1;
        font-size: 24px;
        margin-bottom: 15px;
    }

    .char-section ul {
        list-style-type: disc;
        padding-left: 25px;
        margin-top: 10px;
    }

    .char-section ul li {
        margin-bottom: 10px;
        font-weight: 500;
        font-size: 19px;
    }

    .char-section em {
        color: #555;
        font-size: 17px;
    }
    </style>

    <div class="char-header">
        <h2>📂 Charakterystyka otrzymanych danych</h2>
        <p>W ramach projektu przeanalizowaliśmy trzy główne źródła danych, dostarczone w postaci oddzielnych plików. Dane te są podstawą do dalszej analizy rynku oraz skuteczności działań promocyjnych.</p>
    </div>

    <div class="char-section">
        <h3>🧾 Dane rynkowe 2022–2024</h3>
        <p>Zestaw zawiera dane rynkowe dotyczące sprzedaży leków na poziomie ogólnopolskim – pozwala przeanalizować trendy oraz zmiany rynkowe w czasie.</p>
        <p><em>(6 kolumn, 7 590 wierszy)</em></p> <p>Dostępne kolumny:</p>
        <ul>
            <li>Kategoria nazwa</li>
            <li>Rok</li>
            <li>Miesiąc</li>
            <li>Indeks</li>
            <li>Sprzedaż rynek ilość</li>
            <li>Sprzedaż rynek wartość</li>
        </ul>
    </div>

    <div class="char-section">
        <h3>💊 Dane sprzedaży NEUCA (2022,2023,2024)</h3>
        <p>Szczegółowe informacje o sprzedaży leków przez firmę NEUCA, umożliwiające analizę trendów, sezonowości i potencjalnego wpływu działań marketingowych. Dane zostały podzielone na kategorie produktowe:</p>
        <ul>
            <li>Przylepce <em>(20 kolumn, 1 008 046 wierszy)</em></li>
            <li>Preparaty służące do zmniejszenia wagi ciała <em>(20 kolumn, 861 398 wierszy)</em></li>
            <li>Preparaty przeciwwymiotne <em>(20 kolumn, 621 996 wierszy)</em></li>
            <li>Preparaty przeciwalergiczne <em>(20 kolumn, 2 387 235 wierszy)</em></li>
            <li>Leczenie nałogów <em>(20 kolumn, 755 891 wierszy)</em></li>
        </ul>
    </div>

    <div class="char-section">
        <h3>📈 Wnioski promocyjne</h3>
        <p>Pliki zawierają informacje o działaniach promocyjnych – ich typie, czasie trwania i przypisaniu do konkretnych produktów. Są podzielone według kategorii leków:</p>
        <ul>
            <li>Przylepce <em>(17 kolumn, 35 390 wierszy)</em></li>
            <li>Preparaty służące do zmniejszenia wagi ciała <em>(17 kolumn, 24 795 wierszy)</em></li>
            <li>Preparaty przeciwwymiotne <em>(17 kolumn, 7 125 wierszy)</em></li>
            <li>Preparaty przeciwalergiczne <em>(17 kolumn, 36 516 wierszy)</em></li>
            <li>Leczenie nałogów <em>(17 kolumn, 31 348 wierszy)</em></li>
        </ul>
    </div>
                
    <div class="char-section">
        <h3>📊 Podsumowanie wszystkich danych</h3>
        <p>Po połączeniu wszystkich danych otrzymujemy bardzo obszerny zbiór:</p>
        <ul>
            <li><strong>Wnioski promocyjne:</strong> 135 174 wierszy (17 kolumn)</li>
            <li><strong>Dane sprzedażowe NEUCA:</strong> 5 634 566 wierszy (20 kolumn)</li>
            <li><strong>Dane rynkowe:</strong> 7 590 wierszy (6 kolumn)</li>
        </ul>
        <p><strong>Łączna liczba wierszy:</strong> <span style="color:#0d47a1;">5 777 330</span></p>
    </div>
           
    """, unsafe_allow_html=True)

with tab1:
    st.markdown("## ✨ Podsumowanie unikalnych leków i promocji")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Funkcja do cachowania obliczeń unikalnych wartości
    @st.cache_data
    def get_unique_counts(df: pd.DataFrame):
        # Funkcja zostanie ponownie uruchomiona tylko wtedy, gdy 'df' się zmieni (np. jeśli pliki źródłowe zostaną zaktualizowane)
        return {
            'unique_drugs': df['Indeks'].nunique(),
            'unique_promos': df['id promocji'].nunique()
        }

    # Wywołujemy funkcję dla każdego roku i wyświetlamy wyniki
    with col1:
        counts_2022 = get_unique_counts(rok_2022)
        info_card("Unikalne leki 2022", counts_2022['unique_drugs'], "#1abc9c", "💊")
    with col2:
        counts_2022 = get_unique_counts(rok_2022) # Odczyta z cache, bo df jest to samo
        info_card("Promocje 2022", counts_2022['unique_promos'], "#3498db", "🎯")
    with col3:
        counts_2023 = get_unique_counts(rok_2023)
        info_card("Unikalne leki 2023", counts_2023['unique_drugs'], "#2ecc71", "💊")
    with col4:
        counts_2023 = get_unique_counts(rok_2023) # Odczyta z cache
        info_card("Promocje 2023", counts_2023['unique_promos'], "#9b59b6", "🎯")
    with col5:
        counts_2024 = get_unique_counts(rok_2024)
        info_card("Unikalne leki 2024", counts_2024['unique_drugs'], "#f39c12", "💊")
    with col6:
        counts_2024 = get_unique_counts(rok_2024) # Odczyta z cache
        info_card("Promocje 2024", counts_2024['unique_promos'], "#e74c3c", "🎯")

# Zakładamy, że rok_2022, rok_2023, rok_2024 to już załadowane DataFrame'y
# Przykład (w rzeczywistości wczytane z plików):
# rok_2022 = pd.DataFrame(...)
# rok_2023 = pd.DataFrame(...)
# rok_2024 = pd.DataFrame(...)

# Słownik z danymi dla poszczególnych lat
dane_lata = {
    2022: rok_2022,
    2023: rok_2023,
    2024: rok_2024
}

with tab2: # Używamy st.container zamiast tab2, aby kod był samodzielny do testowania
    # Funkcja przygotowująca daty (cachowana)
    @st.cache_data
    def przygotuj_daty_cached(df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        df_copy['Data'] = pd.to_datetime(df_copy['Rok'].astype(str) + '-' + df_copy['Miesiąc'].astype(str) + '-01')
        df_copy['Miesiąc_nazwa'] = df_copy['Miesiąc'].apply(lambda x: calendar.month_name[x])
        return df_copy

    # Funkcja rysująca wykres liniowy (cachowana)
    @st.cache_data
    def rysuj_wykres_liniowy_cached(df: pd.DataFrame, kolumna: str, tytul: str) -> go.Figure:
        fig = go.Figure()
        for rok in sorted(df['Rok'].unique()):
            df_rok = df[df['Rok'] == rok]
            fig.add_trace(go.Scatter(
                x=df_rok['Data'],
                y=df_rok['sprzedaz_total'],
                mode='lines+markers',
                name=str(rok)
            ))
        fig.update_layout(
            title=tytul,
            xaxis_title='Miesiąc',
            yaxis_title=kolumna,
            yaxis_tickformat=',',
            xaxis=dict(tickformat='%b'),
            yaxis_range=[0, df['sprzedaz_total'].max() * 1.1],
            hovermode='x unified'
        )
        return fig

    # Funkcja do generowania tabel top/bottom
    def tabela_top_bottom(df, rok, kolumna, st_col):
        st_col.markdown(f"### {rok} — Top 3 miesiące")
        top3 = df.nlargest(3, 'sprzedaz_total')[['Miesiąc_nazwa', 'sprzedaz_total']]
        top3['sprzedaz_total'] = top3['sprzedaz_total'].map('{:,.0f}'.format)
        st_col.table(top3.rename(columns={"Miesiąc_nazwa": "Miesiąc", "sprzedaz_total": kolumna}))

        st_col.markdown(f"### {rok} — Bottom 3 miesiące")
        bottom3 = df.nsmallest(3, 'sprzedaz_total')[['Miesiąc_nazwa', 'sprzedaz_total']]
        bottom3['sprzedaz_total'] = bottom3['sprzedaz_total'].map('{:,.0f}'.format)
        st_col.table(bottom3.rename(columns={"Miesiąc_nazwa": "Miesiąc", "sprzedaz_total": kolumna}))

    # ---
    ## Przetwarzanie danych dla łącznej sprzedaży

    st.subheader("Wykresy czasowe łącznej sprzedaży")

    # Użytkownik wybiera, czy chce widzieć sprzedaż wartościową, czy ilościową
    kolumna = st.radio(
        "Wybierz typ danych:",
        ["Sprzedaż budżetowa (wartościowa)", "Sprzedaż ilość"],
        horizontal=True
    )
    # Zmieniamy nazwę kolumny na faktyczną nazwę w DataFrame'ie
    kolumna_df = "Sprzedaż budżetowa" if kolumna == "Sprzedaż budżetowa (wartościowa)" else "Sprzedaż ilość"

    # Cachowanie agregacji danych dla łącznej sprzedaży ze wszystkich lat
    @st.cache_data
    def get_total_sales_monthly_for_all_years(dane_lata_raw: dict, sales_col: str) -> pd.DataFrame:
        all_aggregated_dfs = []
        for rok, df_raw in dane_lata_raw.items():
            sales_monthly_rok = (
                df_raw.groupby(["Rok", "Miesiąc"])
                .agg(sprzedaz_total=(sales_col, "sum"))
                .reset_index()
            )
            all_aggregated_dfs.append(sales_monthly_rok)
        
        df_all_aggregated = pd.concat(all_aggregated_dfs, ignore_index=True)
        return przygotuj_daty_cached(df_all_aggregated)

    # Wywołujemy funkcję agregującą dane dla wszystkich lat
    sprzedaz_mies = get_total_sales_monthly_for_all_years(dane_lata, kolumna_df)

    # Cachowanie pivotowania danych
    @st.cache_data
    def pivot_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
        df['Miesiąc_nazwa_skrot'] = df['Miesiąc'].apply(lambda x: calendar.month_abbr[x])
        pivot_df = df.pivot(index='Miesiąc_nazwa_skrot', columns='Rok', values='sprzedaz_total').reindex(
            calendar.month_abbr[1:13]
        )
        return pivot_df

    sprzedaz_mies_pivot = pivot_monthly_sales(sprzedaz_mies)

    # Cachowanie generowania głównego wykresu
    @st.cache_data
    def create_total_sales_chart(df_pivot: pd.DataFrame, sales_col_name: str) -> go.Figure:
        fig = go.Figure()
        for rok in df_pivot.columns:
            fig.add_trace(go.Scatter(
                x=df_pivot.index,
                y=df_pivot[rok],
                mode='lines+markers',
                name=str(rok)
            ))
        fig.update_layout(
            title=f'Łączna {sales_col_name} — porównanie miesięcy ({min(df_pivot.columns)}–{max(df_pivot.columns)})',
            xaxis_title='Miesiąc',
            yaxis_title=sales_col_name,
            yaxis_tickformat=',',
            hovermode='x unified',
            legend_title='Rok'
        )
        return fig

    fig = create_total_sales_chart(sprzedaz_mies_pivot, kolumna)
    st.plotly_chart(fig, use_container_width=True)

    # Wyświetlanie tabel Top/Bottom dla każdego roku
    cols = st.columns(len(dane_lata))
    for i, (rok, _) in enumerate(dane_lata.items()): # Iterujemy po kluczach słownika dla roku
        # Cachowanie filtrowania dla tabel top/bottom
        @st.cache_data
        def get_yearly_sales_for_table_from_aggregated(df_sales_monthly_aggregated: pd.DataFrame, target_year: int) -> pd.DataFrame:
            return df_sales_monthly_aggregated[df_sales_monthly_aggregated['Rok'] == target_year]

        df_rok_for_table = get_yearly_sales_for_table_from_aggregated(sprzedaz_mies, rok)
        tabela_top_bottom(df_rok_for_table, rok, kolumna, cols[i])
        
        
    st.subheader("Sprzedaż wg kategorii (rozdzielnie dla każdego roku)")

    @st.cache_data
    def agreguj_sprzedaz_kategorie(dane_lata_raw: dict, sales_col: str) -> pd.DataFrame:
        df_list = []
        for rok, df_raw in dane_lata_raw.items():
            df_agg = (
                df_raw.groupby("Kategoria nazwa")
                .agg(sprzedaz_total=(sales_col, "sum"))
                .reset_index()
            )
            df_agg["Rok"] = rok
            df_list.append(df_agg)
        return pd.concat(df_list, ignore_index=True)

    df_kategorie = agreguj_sprzedaz_kategorie(dane_lata, kolumna_df)

    @st.cache_data
    
    def rysuj_wykres_kategorie(df: pd.DataFrame, sales_col_name: str) -> go.Figure:
        fig = go.Figure()
        for rok in sorted(df["Rok"].unique()):
            df_rok = df[df["Rok"] == rok].sort_values("sprzedaz_total", ascending=False)
            fig.add_trace(go.Bar(
                x=df_rok["Kategoria nazwa"],
                y=df_rok["sprzedaz_total"],
                name=str(rok),
                text=df_rok["sprzedaz_total"].map(lambda x: f"{x:,.0f}"),
                textposition='outside'  # lub 'auto', 'inside', 'outside', 'none'
            ))
        fig.update_layout(
            title=f"Sprzedaż wg kategorii — porównanie lat",
            xaxis_title="Kategoria",
            yaxis_title=sales_col_name,
            barmode='group',
            xaxis_tickangle=-45,
            yaxis_tickformat=',',
            legend_title="Rok",
            margin=dict(t=100, b=150) 
        )
        max_val = df["sprzedaz_total"].max() * 1.5
        fig.update_yaxes(range=[0, max_val])
        return fig

        
    fig_kategorie = rysuj_wykres_kategorie(df_kategorie, kolumna)
    st.plotly_chart(fig_kategorie, use_container_width=True)
with tab3:
    # ======= Użytkownik wybiera sposób sortowania TOP 10 =======
    sortowanie_po = st.selectbox("Sortuj TOP 10 wg", ["Sprzedaż ilość", "Sprzedaż budżetowa"])

    # ======= Pasek wizualny (nie wymaga cachowania, to prosta funkcja) =======
    def wizualny_pasek(wartosc, max_wartosc, szerokosc=25, znak="▇"):
        proporcja = wartosc / max_wartosc if max_wartosc > 0 else 0
        liczba_znakow = int(proporcja * szerokosc)
        return znak * liczba_znakow + " " * (szerokosc - liczba_znakow)

    # ======= Funkcja do przetwarzania danych jednego roku (cachowana) =======
    @st.cache_data
    def przygotuj_top5_cached(df_roczny: pd.DataFrame, grupuj_po: str, sort_by_col: str) -> pd.DataFrame:
        # Ta funkcja zostanie uruchomiona ponownie tylko wtedy, gdy zmieni się df_roczny, grupuj_po lub sort_by_col
        df_gr = (
            df_roczny.groupby(grupuj_po)[['Sprzedaż ilość', 'Sprzedaż budżetowa']]
            .sum()
            .reset_index()
            .rename(columns={
                'Sprzedaż ilość': 'Sprzedaz_ilosc',
                'Sprzedaż budżetowa': 'Sprzedaz_wartosc'
            })
        )
        # sort_by_col jest teraz argumentem funkcji, więc cache działa poprawnie
        kol_sort = 'Sprzedaz_ilosc' if sort_by_col == "Sprzedaż ilość" else 'Sprzedaz_wartosc'
        return df_gr.sort_values(by=kol_sort, ascending=False).head(5)

    # ======= TOP 5 PRODUCENCI: wyświetlenie =======
    st.header("TOP 5 producentów wg sprzedaży")

    # Wywołujemy cachowaną funkcję dla każdego roku i wybranej kolumny sortującej
    top10_producenci_per_rok = {
        rok: przygotuj_top5_cached(df, "Producent sprzedażowy kod", sortowanie_po)
        for rok, df in dane_lata.items()
    }

    kolumny = st.columns(len(dane_lata))
    for idx, (rok, df_rok) in enumerate(top10_producenci_per_rok.items()):
        with kolumny[idx]:
            st.markdown(f"### Rok {rok}")
            max_ilosc = df_rok['Sprzedaz_ilosc'].max()
            max_wartosc = df_rok['Sprzedaz_wartosc'].max()

            for _, rzad in df_rok.iterrows():
                producent = rzad["Producent sprzedażowy kod"]
                ilosc = int(rzad["Sprzedaz_ilosc"])
                wartosc = int(rzad["Sprzedaz_wartosc"])
                pasek_ilosc = wizualny_pasek(ilosc, max_ilosc, znak="🟦")
                pasek_wartosc = wizualny_pasek(wartosc, max_wartosc, znak="🟧")
                st.markdown(f"""
    *{producent}* Ilość sprzedanych leków {ilosc:,.0f} szt.  
    {pasek_ilosc}  
    Wartość sprzedanych leków {wartosc:,.0f} zł  
    {pasek_wartosc}  
    """)

    # ======= TOP 5 PRODUKTY: wyświetlenie =======
    st.header("TOP 5 leków wg sprzedaży")

    # Wywołujemy cachowaną funkcję dla każdego roku i wybranej kolumny sortującej
    top10_produkty_per_rok = {
        rok: przygotuj_top5_cached(df, "Indeks", sortowanie_po)
        for rok, df in dane_lata.items()
    }

    kolumny_p = st.columns(len(dane_lata))
    for idx, (rok, df_rok) in enumerate(top10_produkty_per_rok.items()):
        with kolumny_p[idx]:
            st.markdown(f"### Rok {rok}")
            max_ilosc = df_rok['Sprzedaz_ilosc'].max()
            max_wartosc = df_rok['Sprzedaz_wartosc'].max()

            for _, rzad in df_rok.iterrows():
                indeks = rzad["Indeks"]
                ilosc = int(rzad["Sprzedaz_ilosc"])
                wartosc = int(rzad["Sprzedaz_wartosc"])
                pasek_ilosc = wizualny_pasek(ilosc, max_ilosc, znak="🟦")
                pasek_wartosc = wizualny_pasek(wartosc, max_wartosc, znak="🟧")
                st.markdown(f"""
    *{indeks}* Ilość sprzedanych leków {ilosc:,.0f} szt.  
    {pasek_ilosc}  
    Wartość sprzedanych leków {wartosc:,.0f} zł  
    {pasek_wartosc}  
    """)
       
with tab4:
    analiza_wg = st.radio(
        "Wybierz analizę wg:",
        ("Ilość sztuk","Sprzedaż budżetowa (wartość)"),
        horizontal=True
    )

    prog_pareto = st.selectbox("Wybierz próg koncentracji (Pareto)", [70, 80, 90], index=1)

    def suma_wg_roku(dane_lata, kolumna):
        return pd.Series({rok: df[kolumna].sum() for rok, df in dane_lata.items()}).reindex([2022, 2023, 2024])

    st.header("📊 Podsumowanie sprzedaży wg lat")

    left_col, right_col = st.columns([3, 2])

    with left_col:
        kol1, kol2, kol3 = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            df_rok = dane_lata[rok]
            sprzedaz_ilosc = df_rok['Sprzedaż ilość'].sum()
            sprzedaz_wartosc = df_rok['Sprzedaż budżetowa'].sum()
            kol = [kol1, kol2, kol3][i]

            with kol:
                st.markdown(f"""
                    <div style="font-size:30px; font-weight:bold; margin-bottom:3px;">Rok {rok}</div>
                    <div style="font-size:25px;">Ilość sztuk:<br><b>{int(sprzedaz_ilosc):,}</b></div>
                    <div style="font-size:25px;">Wartość sprzedaży:<br><b>{sprzedaz_wartosc:,.2f} zł</b></div>
                """, unsafe_allow_html=True)

    with right_col:
        kolumna_wykres = 'Sprzedaż budżetowa' if analiza_wg == "Sprzedaż budżetowa (wartość)" else 'Sprzedaż ilość'
        y_label = "Sprzedaż budżetowa [zł]" if analiza_wg == "Sprzedaż budżetowa (wartość)" else "Ilość sprzedanych sztuk"

        wartosci_roczne = suma_wg_roku(dane_lata, kolumna_wykres)

        fig_lata = go.Figure(go.Bar(
            x=wartosci_roczne.index.astype(str),
            y=wartosci_roczne.values,
            marker_color='indianred'
        ))
        fig_lata.update_layout(
            title="Podsumowanie wg lat",
            yaxis_title=y_label,
            xaxis_title="Rok",
            height=300,
            margin=dict(l=10, r=10, t=30, b=30)
        )
        st.plotly_chart(fig_lata, use_container_width=True)

    def wybierz_kolumne_wg(filtr):
        return 'Sprzedaż budżetowa' if filtr == "Sprzedaż budżetowa (wartość)" else 'Sprzedaż ilość'

    def analiza_pareto(df, grupa, filtr, prog):
        kol = wybierz_kolumne_wg(filtr)
        sprzedaz = df.groupby(grupa)[kol].sum().sort_values(ascending=False)
        skumulowana = sprzedaz.cumsum()
        procent = 100 * skumulowana / sprzedaz.sum()
        ograniczone = sprzedaz[procent <= prog].to_frame(name=kol)
        ograniczone['Skumulowany %'] = procent[procent <= prog]
        liczba = len(ograniczone)
        procent_grup = 100 * liczba / len(sprzedaz)
        return liczba, procent_grup, ograniczone, sprzedaz

    kolumna_wykres = wybierz_kolumne_wg(analiza_wg)

    with left_col:
        st.header("📊 Koncentracja sprzedaży wg kategorii")
        kat_cols = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            with kat_cols[i]:
                df_rok = dane_lata[rok]
                liczba_kat, procent_kat, kat_ogran, sprzedaz_kat = analiza_pareto(df_rok, 'Kategoria nazwa', analiza_wg, prog_pareto)
                st.markdown(f"### Rok {rok}")
                st.markdown(
                    f"""
                    <table style='font-size:12px; width:100%;'>
                        <tr><td><b>Liczba kategorii ({prog_pareto}%)</b></td><td>{liczba_kat}</td></tr>
                        <tr><td><b>Procent kategorii</b></td><td>{procent_kat:.1f}%</td></tr>
                    </table>
                    """, unsafe_allow_html=True
                )
                styl_df = kat_ogran.style \
                    .format({kolumna_wykres: "{:,.0f}", 'Skumulowany %': "{:.1f} %"}) \
                    .set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '11px')]},
                        {'selector': 'td', 'props': [('font-size', '11px')]},
                    ])
                st.dataframe(styl_df, use_container_width=True)
        st.write("---")

        st.header("📊 Koncentracja sprzedaży wg promocji")
        promo_cols = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            with promo_cols[i]:
                df_rok = dane_lata[rok]
                liczba_prom, procent_prom, prom_ogran, sprzedaz_prom = analiza_pareto(df_rok, 'Rodzaj promocji poziom 2', analiza_wg, prog_pareto)
                st.markdown(f"### Rok {rok}")
                st.markdown(
                    f"""
                    <table style='font-size:12px; width:100%;'>
                        <tr><td><b>Liczba promocji ({prog_pareto}%)</b></td><td>{liczba_prom}</td></tr>
                        <tr><td><b>Procent promocji</b></td><td>{procent_prom:.1f}%</td></tr>
                    </table>
                    """, unsafe_allow_html=True
                )
                styl_df = prom_ogran.style \
                    .format({kolumna_wykres: "{:,.0f}", 'Skumulowany %': "{:.1f} %"}) \
                    .set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '11px')]},
                        {'selector': 'td', 'props': [('font-size', '11px')]},
                    ])
                st.dataframe(styl_df, use_container_width=True)
        st.write("---")

    with right_col:
        st.header("📊 Wykresy Pareto - kategorie i promocje")

        df_kat_all = []
        for rok in [2022, 2023, 2024]:
            df_rok = dane_lata[rok]
            _, _, _, sprzedaz_kat = analiza_pareto(df_rok, 'Kategoria nazwa', analiza_wg, prog_pareto)
            df_tmp = sprzedaz_kat.reset_index()
            df_tmp['Rok'] = rok
            df_kat_all.append(df_tmp)
        df_kat_all = pd.concat(df_kat_all)

        fig_kat = go.Figure()
        kolory = ['indianred', 'lightsalmon', 'crimson']
        for i, rok in enumerate([2022, 2023, 2024]):
            df_rok = df_kat_all[df_kat_all['Rok'] == rok]
            fig_kat.add_trace(go.Bar(
                x=df_rok['Kategoria nazwa'],
                y=df_rok[kolumna_wykres],
                name=str(rok),
                marker_color=kolory[i]
            ))
        fig_kat.update_layout(
            barmode='group',
            title=f"Sprzedaż wg kategorii",
            yaxis_title=analiza_wg,
            height=350,
            margin=dict(l=10, r=10, t=40, b=40),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_kat, use_container_width=True)

        df_prom_all = []
        for rok in [2022, 2023, 2024]:
            df_rok = dane_lata[rok]
            _, _, _, sprzedaz_prom = analiza_pareto(df_rok, 'Rodzaj promocji poziom 2', analiza_wg, prog_pareto)
            df_tmp = sprzedaz_prom.reset_index()
            df_tmp['Rok'] = rok
            df_prom_all.append(df_tmp)
        df_prom_all = pd.concat(df_prom_all)

        fig_prom = go.Figure()
        for i, rok in enumerate([2022, 2023, 2024]):
            df_rok = df_prom_all[df_prom_all['Rok'] == rok]
            fig_prom.add_trace(go.Bar(
                x=df_rok['Rodzaj promocji poziom 2'],
                y=df_rok[kolumna_wykres],
                name=str(rok),
                marker_color=kolory[i]
            ))
        fig_prom.update_layout(
            barmode='group',
            title=f"Sprzedaż wg promocji",
            yaxis_title=analiza_wg,
            height=350,
            margin=dict(l=10, r=10, t=40, b=40),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_prom, use_container_width=True)
    
with tab5:
    st.title("Analiza udziałów Neuca w rynku i struktura sprzedaży")
    # Filtrujemy dane Neuca i rynek dla 2023 i 2024
    rynek_2023 = rynek[rynek["Rok"] == 2023]
    rynek_2024 = rynek[rynek["Rok"] == 2024]
    
    # Funkcja licząca udziały sumaryczne (roczne)
    def oblicz_udzial(neuca_df, rynek_df):
        neuca_sum = neuca_df[["Sprzedaż ilość", "Sprzedaż budżetowa"]].sum()
        rynek_sum = rynek_df[["Sprzedaż rynek ilość", "Sprzedaż rynek wartość"]].sum()
    
        udzial_ilosc = 100 * neuca_sum["Sprzedaż ilość"] / rynek_sum["Sprzedaż rynek ilość"]
        udzial_wartosc = 100 * neuca_sum["Sprzedaż budżetowa"] / rynek_sum["Sprzedaż rynek wartość"]
        return round(udzial_ilosc, 2), round(udzial_wartosc, 2)
    
    # Obliczamy udziały dla 2023 i 2024
    udzial_ilosc_2023, udzial_wartosc_2023 = oblicz_udzial(rok_2023, rynek_2023)
    udzial_ilosc_2024, udzial_wartosc_2024 = oblicz_udzial(rok_2024, rynek_2024)
    
    
    rok_wybrany = 2024  # domyślnie pokazuj aktualny rok
    
    # wartość i delta zawsze względem 2023
    pokaz_ilosc = udzial_ilosc_2024
    delta_ilosc = udzial_ilosc_2024 - udzial_ilosc_2023
    
    pokaz_wartosc = udzial_wartosc_2024
    delta_wartosc = udzial_wartosc_2024 - udzial_wartosc_2023

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label=f"Udział ilościowy Neuca ({rok_wybrany})",
            value=f"{pokaz_ilosc:.2f}%",
            delta=f"{delta_ilosc:+.2f}%"
        )

    with col2:
        st.metric(
            label=f"Udział wartościowy Neuca ({rok_wybrany})",
            value=f"{pokaz_wartosc:.2f}%",
            delta=f"{delta_wartosc:+.2f} %"
        )

    # Filtrujemy dane Neuca i rynek dla 2023 i 2024
    rynek_2023 = rynek[rynek["Rok"] == 2023]
    rynek_2024 = rynek[rynek["Rok"] == 2024]
    
        # --- Teraz dodajemy wykresy miesięczne z udziałami ---
    
    
    def oblicz_udzial_miesieczny(neuca_df, rynek_df):
        neuca_gr = neuca_df.groupby("Miesiąc").agg({
            "Sprzedaż ilość": "sum",
            "Sprzedaż budżetowa": "sum"
        }).reset_index()
    
        rynek_gr = rynek_df.groupby("Miesiąc").agg({
            "Sprzedaż rynek ilość": "sum",
            "Sprzedaż rynek wartość": "sum"
        }).reset_index()
    
        udzial = pd.merge(neuca_gr, rynek_gr, on="Miesiąc", how="left")
    
        udzial["Udział ilościowy (%)"] = 100 * udzial["Sprzedaż ilość"] / udzial["Sprzedaż rynek ilość"]
        udzial["Udział wartościowy (%)"] = 100 * udzial["Sprzedaż budżetowa"] / udzial["Sprzedaż rynek wartość"]
    
        return udzial
    
    udzial_2023 = oblicz_udzial_miesieczny(rok_2023, rynek_2023)
    udzial_2023["Rok"] = 2023
    
    udzial_2024 = oblicz_udzial_miesieczny(rok_2024, rynek_2024)
    udzial_2024["Rok"] = 2024
    
    udzial_all = pd.concat([udzial_2023, udzial_2024])
    
    fig_ilosc = px.line(
        udzial_all,
        x="Miesiąc",
        y="Udział ilościowy (%)",
        color="Rok",
        markers=True,
        title="Udział ilościowy Neuca w rynku po miesiącach"
    )
    
    fig_wartosc = px.line(
        udzial_all,
        x="Miesiąc",
        y="Udział wartościowy (%)",
        color="Rok",
        markers=True,
        title="Udział wartościowy Neuca w rynku po miesiącach"
    )
    fig_ilosc.update_yaxes(range=[0, 60])
    fig_wartosc.update_yaxes(range=[0, 60])

    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_ilosc, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_wartosc, use_container_width=True)
        
    
    # ID plików Google Drive (te same, które podałaś)
    file_id_wartosc = "1wqe5m2RiMHOjycXywtpDE2Ozmmz9FuC5"
    file_id_ilosc = "1-dC-3eM6MAn0cASAHbdYRQJzXnw5vaMP"

    def download_if_not_exists(file_id, filename):
        if not os.path.exists(filename):
            url = f"https://drive.google.com/uc?id={file_id}"
            gdown.download(url, filename, quiet=False)

    # Pobierz pliki i zapisz pod prostymi nazwami
    download_if_not_exists(file_id_wartosc, "wg_wartosc.png")
    download_if_not_exists(file_id_ilosc, "wg_ilosc.png")

    # Wczytaj obrazy
    img_wartosc = Image.open("wg_wartosc.png")
    img_ilosc = Image.open("wg_ilosc.png")

    with st.expander("📊 Tabela sprzedaży wg wartości (udział wartościowy)", expanded=False):
        st.image(img_wartosc, caption="Tabela sprzedaży wg wartości")
    
    with st.expander("📦 Tabela sprzedaży wg ilości (udział ilościowy)", expanded=False):
        st.image(img_ilosc, caption="Tabela sprzedaży wg ilości")


def download_if_not_exists(file_id, filename):
    """Pobiera plik z Google Drive jeśli nie istnieje lokalnie."""
    if not os.path.exists(filename):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filename, quiet=False)

def show_dashboard_block(df: pd.DataFrame, title: str):
    """Wyświetla dashboardową cegiełkę z podsumowaniem danych."""

    # Podstawowe info o danych
    rows = df.shape[0]
    cols = df.shape[1]

    # Top 3 miesiące rozpoczęcia i zakończenia promocji (jeśli kolumny są)
    top_start = df['Miesiąc rozpoczęcia'].value_counts().nlargest(3) if 'Miesiąc rozpoczęcia' in df.columns else pd.Series()
    top_end = df['Miesiąc zakończenia'].value_counts().nlargest(3) if 'Miesiąc zakończenia' in df.columns else pd.Series()

    # Wyłączenie rabatowania (jeśli kolumna istnieje)
    wył_rabatowania = None
    if "Wyłączenie rabatowania" in df.columns:
        wył_rabatowania = df["Wyłączenie rabatowania"].value_counts().sort_index()

    # Wybór kolumn do statystyk (tylko te które są w df)
    wybrane_kolumny = [
        "sprzedaż_sztuki", "Rabat promocyjny %", "Rabat kwotowy",
        'Neuca_sprzedaz_przed', 'Sprzedaz_rynkowa_przed',
        'Neuca_sprzedaz_przed_rok_wczesniej', 'Neuca_sprzedaz_w_trakcie_rok_wczesniej',
        'Neuca_sprzedaz_po_rok_wczesniej', 'Sprzedaz_rynkowa_przed_rok_wczesniej',
        'Sprzedaz_rynkowa_w_trakcie_rok_wczesniej', 'Sprzedaz_rynkowa_po_rok_wczesniej'
    ]
    kolumny_dostepne = [k for k in wybrane_kolumny if k in df.columns]
    statystyki = df[kolumny_dostepne].describe().loc[["mean", "50%", "std", "max"]].T if kolumny_dostepne else pd.DataFrame()
    statystyki.index.name = "Wskaźnik"
    if not statystyki.empty:
    # Formatowanie liczb w stylu "12 345", z zaokrągleniem do 2 miejsc po przecinku
     statystyki_formatowane = statystyki.style.format(lambda x: f"{x:,.2f}".replace(",", " ").replace(".00", ""))
    else:
     st.info("Brak dostępnych kolumn do obliczenia statystyk.")

    rabat_wazony = None
    if "Rabat promocyjny %" in df.columns and "sprzedaż_sztuki" in df.columns:
        rabat_df = df[["Rabat promocyjny %", "sprzedaż_sztuki"]].copy()
        rabat_df["Rabat promocyjny %"] = rabat_df["Rabat promocyjny %"].abs()
        if rabat_df["sprzedaż_sztuki"].sum() > 0:
            rabat_wazony = (rabat_df["Rabat promocyjny %"] * rabat_df["sprzedaż_sztuki"]).sum() / rabat_df["sprzedaż_sztuki"].sum()
            rabat_wazony = round(rabat_wazony, 2)

    # Wyświetlanie nagłówka i podstawowych info
    st.markdown(f"""
    <div style='border: 2px solid #6c757d; border-radius: 15px; padding: 15px; background-color: #f0f4ff; box-shadow: 2px 2px 5px rgba(100, 149, 237, 0.3);'>
        <h3 style='color: #4169E1;'>📊 Dane: {title}</h3>
        <p style='color: black;'><b>Liczba wierszy:</b> {rows}</p>
        <p style='color: black;'><b>Liczba kolumn:</b> {cols}</p>
        {"<p style='color: black; font-weight: bold;'>🎯 Średni rabat ważony: " + str(rabat_wazony) + " %</p>" if rabat_wazony is not None else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Jeśli rabat ważony się nie wyliczył
    if rabat_wazony is None:
        st.warning(f"Brak danych do obliczenia średniego rabatu dla {title}.")
    
    # 🔄 Sekcja wyłączenia rabatowania
    if wył_rabatowania is not None:
        liczba_wylaczen = wył_rabatowania.get(1, 0)
        df_filtered = wył_rabatowania.drop(labels=[0, 1], errors='ignore')
        
        st.markdown("""
        <div style='border: 2px solid #6c757d; border-radius: 15px; padding: 15px; margin-top: 20px; background-color: #fefefe; box-shadow: 1px 1px 4px rgba(100, 100, 100, 0.2);'>
            <h4 style='color: #333;'>🔄 Wyłączenie rabatowania</h4>
            <p style='color: black; font-weight: bold;'>W tym te wiersze, w których mamy wyłączenie rabatowania – nie naliczają się warunki handlowe apteki.</p>
            <p style='color: black;'>- Liczba wierszy z wyłączeniem rabatowania = 1: <b>{}</b></p>
        </div>
        """.format(liczba_wylaczen), unsafe_allow_html=True)
    
        if not df_filtered.empty:
            st.dataframe(df_filtered.rename_axis("Wartość").reset_index(name="Liczba"))


    month_names = {
        1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień", 5: "Maj", 6: "Czerwiec",
        7: "Lipiec", 8: "Sierpień", 9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"
    }

    def show_podium_months(series, title):
        if series.empty:
            st.write(f"Brak danych dla {title}")
            return

        # Zamiana indeksu na pełne nazwy miesięcy
        months = [month_names.get(m, str(m)) for m in series.index]
        counts = series.values

        # Bezpiecznie: jeśli jest mniej niż 3, uzupełniamy puste miejsca
        while len(months) < 3:
            months.append("-")
            counts = list(counts) + [0]

        podium_html = f"""
        <style>
            .podium {{
                display: flex;
                justify-content: center;
                align-items: flex-end;
                gap: 20px;
                margin-bottom: 20px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .place {{
                text-align: center;
                color: #333;
                border-radius: 10px;
                padding: 10px;
                background: #e8f0fe;
                box-shadow: 2px 2px 6px rgba(65, 105, 225, 0.3);
            }}
            .first {{
                font-size: 1.6rem;
                font-weight: 700;
                height: 150px;
                background: #4169E1;
                color: white;
                flex: 1.5;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding-bottom: 15px;
                border-radius: 12px;
            }}
            .second {{
                font-size: 1.2rem;
                font-weight: 600;
                height: 120px;
                background: #89a9f7;
                color: white;
                flex: 1.2;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding-bottom: 10px;
                border-radius: 10px;
            }}
            .third {{
                font-size: 1rem;
                font-weight: 600;
                height: 100px;
                background: #c1cfff;
                color: #333;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                padding-bottom: 10px;
                border-radius: 10px;
            }}
            .place .rank {{
                font-weight: 900;
                font-size: 1.4rem;
                margin-bottom: 5px;
            }}
            .place .month {{
                font-weight: 700;
            }}
            .place .count {{
                font-size: 1rem;
                opacity: 0.8;
            }}
        </style>
        <div class="podium">
            <div class="second place">
                <div class="rank">2</div>
                <div class="month">{months[1]}</div>
                <div class="count">Liczba: {counts[1]}</div>
            </div>
            <div class="first place">
                <div class="rank">1</div>
                <div class="month">{months[0]}</div>
                <div class="count">Liczba: {counts[0]}</div>
            </div>
            <div class="third place">
                <div class="rank">3</div>
                <div class="month">{months[2]}</div>
                <div class="count">Liczba: {counts[2]}</div>
            </div>
        </div>
        """

        st.markdown(f"### 📅 Top 3 miesiące: {title}", unsafe_allow_html=True)
        st.markdown(podium_html, unsafe_allow_html=True)

    show_podium_months(top_start, "rozpoczęcia promocji")
    show_podium_months(top_end, "zakończenia promocji")

    if not statystyki.empty:
        st.markdown("### 📊 Statystyki wybranych wskaźników")
        st.dataframe(statystyki_formatowane)
    else:
        st.write("Brak danych statystycznych dla wybranych kolumn")

    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    # Pobierz pliki jeśli brak
    file_id1 = "1AUcE2y6psfWJeNbq3YdtlA1E2GtIqfbi"
    filename1 = "waga.csv"
    download_if_not_exists(file_id1, filename1)
    waga = pd.read_csv(filename1)

    file_id2 = "1UUBMz0J6yADel-MV8RqMCBqsGmH6aTMH"
    filename2 = "przylepce.csv"
    download_if_not_exists(file_id2, filename2)
    przylepce = pd.read_csv(filename2)

    col1, col2, col3 = st.columns(3)

    with col1:
        show_dashboard_block(waga, "Waga")

    with col2:
        show_dashboard_block(przylepce, "Przylepce")
    
    with col3:
        # Obliczenia udziałów
        czestosc = waga['Rodzaj promocji'].value_counts(normalize=True) * 100
        sprzedaz = waga.groupby('Rodzaj promocji')['sprzedaż_sztuki'].sum()
        sprzedaz_total = waga['sprzedaż_sztuki'].sum()
        udzial_sztuki = (sprzedaz / sprzedaz_total) * 100
        
        # Złączenie wyników
        podsumowanie = pd.DataFrame({
            "Częstość (%)": czestosc,
            "Sprzedaż (%)": udzial_sztuki
        }).round(2)
        
        # Dodanie kolumny opisowej: "12.3% (23.4%)"
        podsumowanie["Udział"] = podsumowanie.apply(
            lambda row: f"{row['Częstość (%)']}% ({row['Sprzedaż (%)']}%)", axis=1
        )
        
        # Sortowanie wg częstotliwości
        podsumowanie = podsumowanie.sort_values(by="Częstość (%)", ascending=False)
        
        # Podział na podium i resztę
        top3 = podsumowanie.head(3)
        reszta = podsumowanie.iloc[3:].copy()
        reszta.reset_index(inplace=True)
        reszta = reszta[["Rodzaj promocji", "Udział"]].rename(columns={"Udział": "Udział %"})
        
        # PODIUM
        st.markdown("### 🏆 Najczęstsze rodzaje promocji - dla preparatów zmniejszających wagę - (i ich udziały w sprzedaży promocyjnej) ")
        colors = ["#E3F2FD", "#F3E5F5", "#FFF3E0"]
        medale = ["🥇", "🥈", "🥉"]
        
        cols = st.columns(3)
        for i, (col, (nazwa, rzad)) in enumerate(zip(cols, top3.iterrows())):
            col.markdown(f"""
            <div style='background-color: {colors[i]}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 2px 2px 8px rgba(0,0,0,0.15);'>
                <h4 style='color: black;'>{medale[i]} {nazwa}: {rzad["Udział"]}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # RESZTA
        st.markdown("### 📋 Pozostałe rodzaje promocji")
        st.dataframe(reszta, use_container_width=True)


        # Udział procentowy sprzedaży D19
        d19_df = waga[waga["Producent sprzedażowy kod"] == 'D19']
        # Liczba unikalnych leków po indeksie
        liczba_lekow = d19_df["Indeks"].nunique()
        # Suma sprzedaży sztuk 
        sprzedaz_calkowita = waga["sprzedaż_sztuki"].sum()
        sprzedaz_d19 = d19_df["sprzedaż_sztuki"].sum()
        udzial_d19 = round((sprzedaz_d19 / sprzedaz_calkowita) * 100, 2) if sprzedaz_calkowita != 0 else 0
        # Filtr dla leku o indeksie 69065
        sprzedaz_leku = waga[waga["Indeks"] == 69065]["sprzedaż_sztuki"].sum()
        udzial_l = round((sprzedaz_leku / sprzedaz_calkowita) * 100, 2)
        # Tworzenie grafu
        graf = graphviz.Digraph()
        graf.node("Producent", " Producent: D19\n(jedyny uczestniczący w promocji Synoptis)",shape='folder', style='filled', fillcolor='#E0F7FA')
        graf.node("Udział", "Udział promocyjny (Synoptis)\n w sprzedazy leków największy mimo bycia najrzadszą kategorią",shape='folder', style='filled', fillcolor='#FFF3E0')
        graf.node("Typ zamówienia", "W tej promocji jedynie \n zamówienia modemowe i telefoniczne", shape='folder', style='filled', fillcolor='#FFF3E0')
        graf.node("Produkty", f"💊 Produkty D19:\n{liczba_lekow} unikalnych",shape='folder', style='filled', fillcolor='#F3E5F5')
        graf.node("Sprzedaż", f"📈 Sprzedaż produktów D19:\n{sprzedaz_d19:,} sztuk\n({udzial_d19}% ogółem)",shape='folder', style='filled', fillcolor='#E1F5FE')
        graf.node("Przykład", "📌 Przykład leku:\nIndeks 69065\n(należy do D19)", shape='folder', style='filled', fillcolor='#FFEBEE')
        graf.node("Lek", f"📌 \nIndeks 69065\n sprzedaż {sprzedaz_leku}, a jego udział {udzial_l}%", shape='folder', style='filled', fillcolor='#FFEBEE')
        graf.edge("Producent", "Typ zamówienia", style='dashed')
        graf.edge("Producent", "Udział", style='dashed')
        graf.edge("Producent", "Produkty", style='dashed')
        graf.edge("Produkty", "Sprzedaż", style='dashed')
        graf.edge("Produkty", "Przykład", style='dashed')
        graf.edge("Przykład", "Lek", style='dashed')
        # Wyświetlenie
        st.graphviz_chart(graf)



