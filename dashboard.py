import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import gdown
import gc
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as mtick
import calendar
from dateutil.relativedelta import relativedelta
import requests
from io import BytesIO

st.set_page_config(page_title="Analiza danych sprzedażowych lata 2022-2024", layout="wide")
st.title("📊 Dashboard marketingowy Neuca")
tab1, tab2, tab3, tab4,tab5 = st.tabs(["📈 Przegląd lat 2022-2024", "📈 Wykresy czasowe", "🏆 Top 10","Analiza Pareto",'Udziały rynkowe'])
@st.cache_data(show_spinner=True)
def load_parquet_from_gdrive(id, filename):
    if not os.path.exists(filename):
        gdown.download(f"https://drive.google.com/uc?id={id}", filename, quiet=False)
    return pd.read_parquet(filename)

rok_2022 = load_parquet_from_gdrive("1dNNjD4_nAjEfdOCmXRW2IkJRWrmZOKv2", "rok_2022.parquet")
rok_2023 = load_parquet_from_gdrive("12mhaL_5ii73QTuNBDLj-g_8m6hW4Pt62", "rok_2023.parquet")
rok_2024 = load_parquet_from_gdrive("1sFG4A0j4qvBeGleAChgQPPc3nSkjfgNf", "rok_2024.parquet")


@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1-ht0X_NyVlJI8hOxxzKp6Z-4c7uvR-z7/export?format=csv"
    return pd.read_csv(url)
rynek = load_data()

# Ładowanie danych
rok_2022 = pd.read_parquet(BytesIO(response1.content))
rok_2023 = pd.read_parquet(BytesIO(response2.content))
rok_2024 = pd.read_parquet(BytesIO(response3.content))



# --- Funkcje pomocnicze ---
def info_card(title, value, color, icon):
        st.markdown(f"""
        <div style='padding: 15px; background-color: {color}; border-radius: 12px; text-align: center; color: white;'>
            <div style='font-size: 22px;'>{icon}</div>
            <div style='font-size: 16px; font-weight: bold;'>{title}</div>
            <div style='font-size: 20px;'>{value}</div>
        </div>
        """, unsafe_allow_html=True)
    
# 🔢 Agregujemy dane do jednej tabeli
def przygotuj_statystyki(df_2022, df_2023, df_2024):
    lata = [2022, 2023, 2024]
    frames = [df_2022, df_2023, df_2024]
    rekordy = []

    for df, rok in zip(frames, lata):
        df = df.copy()
        df = df[(df['Sprzedaż ilość'] > 0) & (df['Sprzedaż budżetowa'] > 0)]
        df['cena_jednostkowa'] = df['Sprzedaż budżetowa'] / df['Sprzedaż ilość']
        grupy = df.groupby('Kategoria nazwa')['cena_jednostkowa']
        for kat, dane in grupy:
            rekordy.append({
                'Kategoria': kat,
                'Rok': rok,
                'Średnia': dane.mean(),
                'Mediana': dane.median()
            })

    return pd.DataFrame(rekordy)


with tab1:
        st.markdown("## ✨ Podsumowanie unikalnych leków i promocji")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            info_card("Unikalne leki 2022", rok_2022['Indeks'].nunique(), "#1abc9c", "💊")
        with col2:
            info_card("Promocje 2022", rok_2022['id promocji'].nunique(), "#3498db", "🎯")
        with col3:
            info_card("Unikalne leki 2023", rok_2023['Indeks'].nunique(), "#2ecc71", "💊")
        with col4:
            info_card("Promocje 2023", rok_2023['id promocji'].nunique(), "#9b59b6", "🎯")
        with col5:
            info_card("Unikalne leki 2024", rok_2024['Indeks'].nunique(), "#f39c12", "💊")
        with col6:
            info_card("Promocje 2024", rok_2024['id promocji'].nunique(), "#e74c3c", "🎯")


with tab2:
    # === FUNKCJE POMOCNICZE ===
    

    def przypisz_typ_sprzedazy(df):
        def typ_sprzedazy(row):
            if pd.notna(row['Sprzedaż budżetowa ZP']) and row['Sprzedaż budżetowa ZP'] > 0:
                return 'ZP'
            elif pd.notna(row['Sprzedaż budżetowa promocyjna']) and row['Sprzedaż budżetowa promocyjna'] > 0:
                return 'Promocyjna'
            else:
                return 'Normalna'
        df['Typ sprzedaży'] = df.apply(typ_sprzedazy, axis=1)
        return df
    

    def przygotuj_daty(df):
        df['Data'] = pd.to_datetime(df['Rok'].astype(str) + '-' + df['Miesiąc'].astype(str) + '-01')
        df['Miesiąc_nazwa'] = df['Miesiąc'].apply(lambda x: calendar.month_name[x])
        return df
    
    def rysuj_wykres_liniowy(df, kolumna, tytul):
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
    
    def tabela_top_bottom(df, rok, kolumna, st_col):
        st_col.markdown(f"### {rok} — Top 3 miesiące")
        top3 = df.nlargest(3, 'sprzedaz_total')[['Miesiąc_nazwa', 'sprzedaz_total']]
        top3['sprzedaz_total'] = top3['sprzedaz_total'].map('{:,.0f}'.format)
        st_col.table(top3.rename(columns={"Miesiąc_nazwa": "Miesiąc", "sprzedaz_total": kolumna}))
    
        st_col.markdown(f"### {rok} — Bottom 3 miesiące")
        bottom3 = df.nsmallest(3, 'sprzedaz_total')[['Miesiąc_nazwa', 'sprzedaz_total']]
        bottom3['sprzedaz_total'] = bottom3['sprzedaz_total'].map('{:,.0f}'.format)
        st_col.table(bottom3.rename(columns={"Miesiąc_nazwa": "Miesiąc", "sprzedaz_total": kolumna}))
    
    # === WSTĘPNE PRZETWARZANIE ===
    
    rok_2022 = przypisz_typ_sprzedazy(rok_2022)
    rok_2023 = przypisz_typ_sprzedazy(rok_2023)
    rok_2024 = przypisz_typ_sprzedazy(rok_2024)
    df_all = pd.concat([rok_2022, rok_2023, rok_2024], ignore_index=True)
    
    st.subheader("Wykresy czasowe sprzedaży budżetowej")
    
    tryb_sprzedazy = st.radio(
        "Wybierz typ danych:",
        ["Sprzedaż budżetowa (wartościowa)", "Sprzedaż ilościowa"],
        horizontal=True
    )
    
    kolumna = "Sprzedaż budżetowa" if tryb_sprzedazy == "Sprzedaż budżetowa (wartościowa)" else "Sprzedaż ilość"
    
    wybor = st.radio(
        "Wybierz rodzaj wykresu:",
        ["Łączna sprzedaż", "Sprzedaż wg typu sprzedaży"],
        horizontal=True
    )
    
    # === ŁĄCZNA SPRZEDAŻ ===
    if wybor == "Łączna sprzedaż":
        sprzedaz_mies = (
            df_all.groupby(["Rok", "Miesiąc"])
            .agg(sprzedaz_total=(kolumna, "sum"))
            .reset_index()
        )
        sprzedaz_mies = przygotuj_daty(sprzedaz_mies)
    
        # Przygotowanie danych w układzie Miesiąc x Rok
        sprzedaz_mies['Miesiąc_nazwa'] = sprzedaz_mies['Miesiąc'].apply(lambda x: calendar.month_abbr[x])
        sprzedaz_mies_pivot = sprzedaz_mies.pivot(index='Miesiąc_nazwa', columns='Rok', values='sprzedaz_total').reindex(
            calendar.month_abbr[1:13]
            )

        fig = go.Figure()
        for rok in sprzedaz_mies_pivot.columns:
            fig.add_trace(go.Scatter(
                x=sprzedaz_mies_pivot.index,
                y=sprzedaz_mies_pivot[rok],
                mode='lines+markers',
                name=str(rok)
                ))

        fig.update_layout(
            title=f'Łączna {kolumna} — porównanie miesięcy (2022–2024)',
            xaxis_title='Miesiąc',
            yaxis_title=kolumna,
            yaxis_tickformat=',',
            hovermode='x unified',
            legend_title='Rok'
            )

        st.plotly_chart(fig, use_container_width=True)
    
        cols = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            df_rok = sprzedaz_mies[sprzedaz_mies['Rok'] == rok]
            tabela_top_bottom(df_rok, rok, kolumna, cols[i])
    
    # === SPRZEDAŻ WG TYPU — w 3 kolumnach równolegle ===
    elif wybor == "Sprzedaż wg typu sprzedaży":
        st.markdown("### Wykresy wg typu sprzedaży dla poszczególnych lat")
        
        cols = st.columns(3)  # 3 kolumny równolegle
        
        for i, (rok, df) in enumerate(zip([2022, 2023, 2024], [rok_2022, rok_2023, rok_2024])):
            miesieczna_sprzedaz = (
                df.groupby(['Rok', 'Miesiąc', 'Typ sprzedaży'])[kolumna]
                .sum().unstack(fill_value=0).sort_index()
            )
            miesieczna_sprzedaz.index = [
                pd.to_datetime(f"{rok}-{m:02d}-01") for _, m in miesieczna_sprzedaz.index
            ]
            fig = go.Figure()
            for typ in miesieczna_sprzedaz.columns:
                fig.add_trace(go.Scatter(
                    x=miesieczna_sprzedaz.index,
                    y=miesieczna_sprzedaz[typ],
                    mode='lines+markers',
                    name=typ
                ))
            fig.update_layout(
                title=f'{kolumna} wg typu sprzedaży ({rok})',
                xaxis_title='Miesiąc',
                yaxis_title=kolumna,
                yaxis_tickformat=',',
                xaxis=dict(tickformat='%b'),
                yaxis_range=[0, miesieczna_sprzedaz.values.max() * 1.1],
                legend_title='Typ sprzedaży',
                hovermode='x unified',
                margin=dict(t=40, b=40)
            )
            cols[i].plotly_chart(fig, use_container_width=True)

with tab3:
  
    def top10_producenci_promocje(df, typ_sprzedazy="Ilość"):
        kolumna_sprzedazy = "Sprzedaż ilość" if typ_sprzedazy == "Ilość" else "Sprzedaż budżetowa"
        # Grupujemy po producencie
        df_gr = (
            df.groupby('Producent sprzedażowy kod')
            .agg(
                Sprzedaz_sum=(kolumna_sprzedazy, 'sum'),
                Liczba_rodzaj_promocji=pd.NamedAgg(column='Rodzaj promocji poziom 2', aggfunc=lambda x: x.nunique()),
                Liczba_id_promocji=pd.NamedAgg(column='id promocji', aggfunc=lambda x: x.nunique())
            )
            .reset_index()
        )
        df_gr = df_gr.sort_values(by='Sprzedaz_sum', ascending=False).head(10)
        return df_gr
    
    def formatuj_producentow_lista(df, typ=None):
     lista = []
     for i, row in enumerate(df.itertuples(), start=1):
        sprzedaz = f"{row.Sprzedaz_sum:,.0f}".replace(",", " ")
        promocje = row.Liczba_rodzaj_promocji
        id_promocji = row.Liczba_id_promocji
        jednostka = "szt." if typ == "Ilość" else "zł"
        lista.append(f"{i}. {row._1} — {sprzedaz} {jednostka} | Rodzaje promocji: {promocje} | Unikalne ID promocji: {id_promocji}")
     return lista
    
    typ_sprzedazy_wybrany = st.selectbox("Wybierz typ sprzedaży:", options=["Ilość", "Wartość"])

    top_2022 = top10_producenci_promocje(rok_2022, typ_sprzedazy=typ_sprzedazy_wybrany)
    top_2023 = top10_producenci_promocje(rok_2023, typ_sprzedazy=typ_sprzedazy_wybrany)
    top_2024 = top10_producenci_promocje(rok_2024, typ_sprzedazy=typ_sprzedazy_wybrany)
    
    lista_2022 = formatuj_producentow_lista(top_2022, typ_sprzedazy_wybrany)
    lista_2023 = formatuj_producentow_lista(top_2023, typ_sprzedazy_wybrany)
    lista_2024 = formatuj_producentow_lista(top_2024, typ_sprzedazy_wybrany)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Rok 2022")
        for wiersz in lista_2022:
            st.markdown(wiersz)
    
    with col2:
        st.markdown("### Rok 2023")
        for wiersz in lista_2023:
            st.markdown(wiersz)
    
    with col3:
        st.markdown("### Rok 2024")
        for wiersz in lista_2024:
            st.markdown(wiersz)
    def top10_produkty(df, typ_sprzedazy="Ilość"):
        kolumna = "Sprzedaż ilość" if typ_sprzedazy == "Ilość" else "Sprzedaż budżetowa"
        
        df_filtered = df[df[kolumna] > 0]
        
        top_produkty = (
            df_filtered.groupby(['Producent sprzedażowy kod', 'Indeks'])
            .agg({kolumna: 'sum'})
            .reset_index()
            .sort_values(by=kolumna, ascending=False)
            .head(10)
        )
        
        top_produkty.rename(columns={kolumna: 'Sprzedaz_sum'}, inplace=True)
        return top_produkty
    
    def formatuj_produkty_lista(df, typ_sprzedazy):
        jednostka = "szt." if typ_sprzedazy == "Ilość" else "zł"
        lista = []
        for i, row in enumerate(df.itertuples(), start=1):
            wartosc = f"{row.Sprzedaz_sum:,.0f}".replace(",", " ")
            lista.append(f"{i}. Producent: {row._1}, Produkt: {row.Indeks} — {wartosc} {jednostka}")
        return lista
    
    # Przyjmujemy, że typ_sprzedazy_wybrany jest już zdefiniowany na górze
    
    top_prod_2022 = top10_produkty(rok_2022, typ_sprzedazy=typ_sprzedazy_wybrany)
    top_prod_2023 = top10_produkty(rok_2023, typ_sprzedazy=typ_sprzedazy_wybrany)
    top_prod_2024 = top10_produkty(rok_2024, typ_sprzedazy=typ_sprzedazy_wybrany)
    
    lista_prod_2022 = formatuj_produkty_lista(top_prod_2022, typ_sprzedazy_wybrany)
    lista_prod_2023 = formatuj_produkty_lista(top_prod_2023, typ_sprzedazy_wybrany)
    lista_prod_2024 = formatuj_produkty_lista(top_prod_2024, typ_sprzedazy_wybrany)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Top 10 produktów - Rok 2022")
        for w in lista_prod_2022:
            st.markdown(w)
    
    with col2:
        st.markdown("### Top 10 produktów - Rok 2023")
        for w in lista_prod_2023:
            st.markdown(w)
    
    with col3:
        st.markdown("### Top 10 produktów - Rok 2024")
        for w in lista_prod_2024:
            st.markdown(w)
            
    def srednia_cena_za_sztuke_produkt_transponowana(df, top_produkty):
        df_top = df[df['Indeks'].isin(top_produkty['Indeks'])]
        
        agregat = df_top.groupby('Indeks').agg(
            suma_wart_sprzedazy=('Sprzedaż budżetowa', 'sum'),
            suma_ilosc_sprzedazy=('Sprzedaż ilość', 'sum')
        ).reset_index()
        
        agregat['srednia_cena'] = agregat.apply(
            lambda row: row['suma_wart_sprzedazy'] / row['suma_ilosc_sprzedazy'] if row['suma_ilosc_sprzedazy'] > 0 else 0,
            axis=1
        )
        
        # Utwórz DataFrame z dwoma wierszami i kolumnami jako indeksy produktów
        df_wynik = pd.DataFrame({
            indeks: [indeks, f"{cena:,.2f}".replace(',', ' ')]
            for indeks, cena in zip(agregat['Indeks'], agregat['srednia_cena'])
        }, index=['Indeks', 'Średnia cena [zł]'])
        
        return df_wynik
    
    # Użycie analogicznie jak wcześniej:
    top_2022 = top10_produkty(rok_2022)
    top_2023 = top10_produkty(rok_2023)
    top_2024 = top10_produkty(rok_2024)
    
    tabela_2022 = srednia_cena_za_sztuke_produkt_transponowana(rok_2022, top_2022)
    tabela_2023 = srednia_cena_za_sztuke_produkt_transponowana(rok_2023, top_2023)
    tabela_2024 = srednia_cena_za_sztuke_produkt_transponowana(rok_2024, top_2024)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Średnia cena za sztukę - 2022")
        st.table(tabela_2022)
    
    with col2:
        st.subheader("Średnia cena za sztukę - 2023")
        st.table(tabela_2023)
    
    with col3:
        st.subheader("Średnia cena za sztukę - 2024")
        st.table(tabela_2024)

    


with tab4:
    dane = pd.concat([rok_2022, rok_2023, rok_2024])
    analiza_wg = st.radio(
        "Wybierz analizę wg:",
        ("Sprzedaż budżetowa (wartość)", "Ilość sztuk"),
        horizontal=True  # opcjonalnie: poziomy układ
     )
 
    # --- Funkcja sumująca dane wg roku ---
    def suma_wg_roku(df, kolumna):
        return df.groupby('Rok')[kolumna].sum().reindex([2022, 2023, 2024])
    
    # --- Nagłówek ---
    st.header("📊 Podsumowanie sprzedaży wg lat")
    
    # --- Układ 2 kolumn: lewa - metryki, prawa - wykres ---
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        # 3 kolumny na metryki lat
        kol1, kol2, kol3 = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            df_rok = dane[dane['Rok'] == rok]
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
        # Ustawienia wykresu wg filtru
        if analiza_wg == "Sprzedaż budżetowa (wartość)":
            kolumna_wykres = 'Sprzedaż budżetowa'
            y_label = "Sprzedaż budżetowa [zł]"
        else:
            kolumna_wykres = 'Sprzedaż ilość'
            y_label = "Ilość sprzedanych sztuk"
    
        wartosci_roczne = suma_wg_roku(dane, kolumna_wykres)
    
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
    

        # --- Układ kolumn: dane + wykresy ---
    left_col, right_col = st.columns([3, 2])
    
    # Funkcja pomocnicza: wybór kolumny
    def wybierz_kolumne_wg(filtr):
        return 'Sprzedaż budżetowa' if filtr == "Sprzedaż budżetowa (wartość)" else 'Sprzedaż ilość'
    
    # Funkcje do Pareto dla kategorii i promocji
    def analiza_pareto_kategorie(df, rok, filtr):
        df_rok = df[df['Rok'] == rok]
        kol = wybierz_kolumne_wg(filtr)
        sprzedaz = df_rok.groupby('Kategoria nazwa')[kol].sum().sort_values(ascending=False)
        skumulowana = sprzedaz.cumsum()
        procent = 100 * skumulowana / sprzedaz.sum()
        top_80 = sprzedaz[procent <= 80].to_frame(name=kol)
        top_80['Skumulowany %'] = procent[procent <= 80]
        liczba_kat = len(top_80)
        procent_kat = 100 * liczba_kat / len(sprzedaz)
        return liczba_kat, procent_kat, top_80, sprzedaz
    
    def analiza_pareto_promocje(df, rok, filtr):
        df_rok = df[df['Rok'] == rok]
        kol = wybierz_kolumne_wg(filtr)
        sprzedaz = df_rok.groupby('Rodzaj promocji poziom 2')[kol].sum().sort_values(ascending=False)
        skumulowana = sprzedaz.cumsum()
        procent = 100 * skumulowana / sprzedaz.sum()
        top_80 = sprzedaz[procent <= 80].to_frame(name=kol)
        top_80['Skumulowany %'] = procent[procent <= 80]
        liczba_prom = len(top_80)
        procent_prom = 100 * liczba_prom / len(sprzedaz)
        return liczba_prom, procent_prom, top_80, sprzedaz
    
    kolumna_wykres = wybierz_kolumne_wg(analiza_wg)
    
    with left_col:
        st.header("📊 Koncentracja sprzedaży wg kategorii")
        kat_cols = st.columns(3)
        for i, rok in enumerate([2022, 2023, 2024]):
            with kat_cols[i]:
                liczba_kat, procent_kat, top_kat_80, sprzedaz_kat = analiza_pareto_kategorie(dane, rok, analiza_wg)
                st.markdown(f"### Rok {rok}")
                st.markdown(
                    f"""
                    <table style='font-size:12px; width:100%;'>
                        <tr><td><b>Liczba kategorii (80%)</b></td><td>{liczba_kat}</td></tr>
                        <tr><td><b>Procent kategorii</b></td><td>{procent_kat:.1f}%</td></tr>
                    </table>
                    """, unsafe_allow_html=True
                )
                styl_df = top_kat_80.style \
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
                liczba_prom, procent_prom, top_prom_80, sprzedaz_prom = analiza_pareto_promocje(dane, rok, analiza_wg)
                st.markdown(f"### Rok {rok}")
                st.markdown(
                    f"""
                    <table style='font-size:12px; width:100%;'>
                        <tr><td><b>Liczba promocji (80%)</b></td><td>{liczba_prom}</td></tr>
                        <tr><td><b>Procent promocji</b></td><td>{procent_prom:.1f}%</td></tr>
                    </table>
                    """, unsafe_allow_html=True
                )
                styl_df = top_prom_80.style \
                    .format({kolumna_wykres: "{:,.0f}", 'Skumulowany %': "{:.1f} %"}) \
                    .set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '11px')]},
                        {'selector': 'td', 'props': [('font-size', '11px')]},
                    ])
                st.dataframe(styl_df, use_container_width=True)
        st.write("---")
    
    with right_col:
        st.header("📊 Wykresy Pareto - kategorie i promocje")
    
        # Kategorie - top 10
        df_kat_all = []
        for rok in [2022, 2023, 2024]:
            _, _, _, sprzedaz_kat = analiza_pareto_kategorie(dane, rok, analiza_wg)
            df_tmp = sprzedaz_kat.head(10).reset_index()
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
            title="Pareto wg kategorii",
            yaxis_title=analiza_wg,
            height=350,
            margin=dict(l=10, r=10, t=40, b=40),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_kat, use_container_width=True)
    
        # Promocje - top 10
        df_prom_all = []
        for rok in [2022, 2023, 2024]:
            _, _, _, sprzedaz_prom = analiza_pareto_promocje(dane, rok, analiza_wg)
            df_tmp = sprzedaz_prom.head(10).reset_index()
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
            title="Pareto wg promocji",
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
        
    
    def przygotuj_miesiac(df):
        df = df.copy()
        df['Data'] = pd.to_datetime(dict(year=df['Rok'], month=df['Miesiąc'], day=1))
        df['Miesiąc_str'] = df['Data'].dt.strftime('%m')
        df['Rok_Miesiąc'] = df['Data'].dt.strftime('%Y-%m')
        return df
    
    def typ_sprzedazy(row):
        if pd.notna(row['Sprzedaż budżetowa ZP']) and row['Sprzedaż budżetowa ZP'] > 0:
            return 'ZP'
        elif pd.notna(row['Sprzedaż budżetowa promocyjna']) and row['Sprzedaż budżetowa promocyjna'] > 0:
            return 'Promocyjna'
        else:
            return 'Normalna'
    
    def przygotuj_tabele(df_rok, rynek_df, typ="Wartość"):
        df_rok = przygotuj_miesiac(df_rok)
        rynek_df = przygotuj_miesiac(rynek_df)
    
        df_rok['Typ sprzedaży'] = df_rok.apply(typ_sprzedazy, axis=1)
        
        if typ == "Wartość":
            kolumna_glowna = "Sprzedaż budżetowa"
            kolumna_rynek = "Sprzedaż rynek wartość"
        else:  # Ilość
            kolumna_glowna = "Sprzedaż ilość"
            kolumna_rynek = "Sprzedaż rynek ilość"
    
        df_rok = df_rok[df_rok[kolumna_glowna] != 0].copy()
    
        neuca_agg_typy = df_rok.groupby(['Miesiąc_str', 'Typ sprzedaży']).agg({kolumna_glowna: 'sum'}).reset_index()
    
        neuca_agg_typy_pivot = neuca_agg_typy.pivot(index='Miesiąc_str', columns='Typ sprzedaży', values=kolumna_glowna).fillna(0)
    
        neuca_agg_typy_pivot = neuca_agg_typy_pivot.rename(columns={
            'ZP': 'ZP',
            'Promocyjna': 'PROMO',
            'Normalna': 'NORMAL'
        }).reset_index()
    
        neuca_total = df_rok.groupby('Miesiąc_str').agg({kolumna_glowna: 'sum'}).rename(columns={kolumna_glowna: 'NEUCA'}).reset_index()
        rynek_total = rynek_df.groupby('Miesiąc_str').agg({kolumna_rynek: 'sum'}).rename(columns={kolumna_rynek: 'RYNEK'}).reset_index()
    
        tabela = rynek_total.merge(neuca_total, on='Miesiąc_str', how='left').merge(neuca_agg_typy_pivot, on='Miesiąc_str', how='left')
    
        tabela['NEUCA%'] = ((tabela['NEUCA'] / tabela['RYNEK']) * 100).round(2)
        # Nowe kolumny procentowe
        tabela['PROMO%'] = (tabela['PROMO'] / tabela['NEUCA'] * 100).round(2)
        tabela['ZP%'] = (tabela['ZP'] / tabela['NEUCA'] * 100).round(2)
        tabela['NORMAL%'] = (tabela['NORMAL'] / tabela['NEUCA'] * 100).round(2)

    
        tabela = tabela.sort_values('Miesiąc_str').reset_index(drop=True)
        return tabela
    
    def formatuj_liczbe(x):
        if pd.isna(x):
            return ""
        return f"{x:,.0f}".replace(",", " ")
    
    def sformatuj_porownanie_wart_z_wart(wart_2024, wart_2023):
        if pd.isna(wart_2024) or pd.isna(wart_2023) or wart_2024 < 0 or wart_2023 < 0:
            return ""
        delta = wart_2024 - wart_2023
        strzalka = "▲" if delta > 0 else "▼"
        kolor = "green" if delta > 0 else "red"
        return f"{formatuj_liczbe(wart_2024)} ({formatuj_liczbe(wart_2023)}) <span style='color:{kolor}'>{strzalka}</span>"
    
    def przygotuj_tabele_porownawcza_surowa(tabela_2024, tabela_2023):
        tabela_2024 = tabela_2024.copy()
        tabela_2023 = tabela_2023.copy()
    
        wspolne_kolumny = [col for col in tabela_2024.columns if col in tabela_2023.columns and col != "Miesiąc_str"]
    
        tabela_2024.columns = ['Miesiąc_str'] + [f"{col}_2024" for col in wspolne_kolumny]
        tabela_2023.columns = ['Miesiąc_str'] + [f"{col}_2023" for col in wspolne_kolumny]
    
        tabela = tabela_2024.merge(tabela_2023, on='Miesiąc_str', how='inner').sort_values('Miesiąc_str')
    
        def sformatuj_wszystko(wart_2024, wart_2023):
            if pd.isna(wart_2024) and pd.isna(wart_2023):
                return ""
            tekst = f"{formatuj_liczbe(wart_2024)} ({formatuj_liczbe(wart_2023)})"
            if (
                pd.notna(wart_2024) and pd.notna(wart_2023)
                and wart_2023 != 0
                and wart_2024 >= 0 and wart_2023 >= 0
            ):
                zmiana = ((wart_2024 - wart_2023) / abs(wart_2023)) * 100
                if zmiana > 0:
                    tekst += f" <span style='color:green'>🔼 {abs(zmiana):.1f}%</span>"
                elif zmiana < 0:
                    tekst += f" <span style='color:red'>🔽 {abs(zmiana):.1f}%</span>"
            return tekst
    
        for col in wspolne_kolumny:
            tabela[col] = tabela.apply(
                lambda row: sformatuj_wszystko(row[f"{col}_2024"], row[f"{col}_2023"]),
                axis=1
            )
    
        tabela.rename(columns={'Miesiąc_str': 'Miesiąc'}, inplace=True)
    
        return tabela[["Miesiąc"] + wspolne_kolumny]
    
    # --- tutaj dodajemy selectbox ---
    typ_sprzedazy_wybrany = st.selectbox(
        "Wybierz typ sprzedaży do analizy:",
        options=["Wartość", "Ilość"]
    )
    
    # --- przygotowanie tabel ---
    tabela_2024 = przygotuj_tabele(rok_2024, rynek_2024, typ=typ_sprzedazy_wybrany)
    tabela_2023 = przygotuj_tabele(rok_2023, rynek_2023, typ=typ_sprzedazy_wybrany)
    
    tabela_porownawcza = przygotuj_tabele_porownawcza_surowa(tabela_2024, tabela_2023)
    
    st.subheader(f"📊 Sprzedaż 2024 (2023) - wg {typ_sprzedazy_wybrany.lower()} sprzedaży")
    st.markdown(tabela_porownawcza.to_html(escape=False, index=False), unsafe_allow_html=True)
