import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from unidecode import unidecode
import streamlit as st
from streamlit_folium import st_folium

# --- Données annuaire locales ---
df_annuaire = pd.read_csv('annuaire.csv')
df_annuaire['departement_norm'] = df_annuaire['departement'].apply(lambda x: unidecode(str(x)).upper())
df_annuaire['region_norm'] = df_annuaire['region'].apply(lambda x: unidecode(str(x)).upper())

# --- Départements depuis fichier local ---
df_deps = pd.read_csv("departements_geographie.csv")
df_deps['geometry'] = df_deps['dep_geography'].apply(wkt.loads)
df_deps['nom_norm'] = df_deps['departement'].apply(lambda x: unidecode(str(x)).upper())
gdf_departements = gpd.GeoDataFrame(df_deps, geometry='geometry', crs="EPSG:4326")

# --- Régions depuis fichier local ---
df_regs = pd.read_csv("region_geographie.csv")
df_regs['geometry'] = df_regs['reg_geography'].apply(wkt.loads)
df_regs['nom_norm'] = df_regs['region'].apply(lambda x: unidecode(str(x)).upper())
gdf_regions = gpd.GeoDataFrame(df_regs, geometry='geometry', crs="EPSG:4326")

# --- Interface Streamlit ---
st.title("Cartes des établissements (Régions et Départements)")
statut_filter = st.radio("Filtrer par statut :", ["Tous", "Public", "Privé"])

if statut_filter != "Tous":
    df_annuaire = df_annuaire[df_annuaire['statut'].str.contains(statut_filter, case=False, na=False)]

# --- Carte départements ---
df_counts_dept = df_annuaire.groupby('departement_norm').size().reset_index(name='nb_etablissements')
gdf_final_dept = gdf_departements.merge(df_counts_dept, left_on='nom_norm', right_on='departement_norm', how='left')
gdf_final_dept['nb_etablissements'] = gdf_final_dept['nb_etablissements'].fillna(0)

m_dept = folium.Map(location=[46.8, 2.5], zoom_start=5, tiles='cartodbpositron')
folium.Choropleth(
    geo_data=gdf_final_dept.__geo_interface__,
    data=gdf_final_dept,
    columns=['departement', 'nb_etablissements'],
    key_on='feature.properties.departement',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Nombre d'établissements"
).add_to(m_dept)

folium.GeoJson(
    gdf_final_dept,
    name='Départements',
    style_function=lambda x: {'fillOpacity': 0, 'color': 'black', 'weight': 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=['departement', 'nb_etablissements'],
        aliases=['Département', 'Établissements'])
).add_to(m_dept)

st.subheader("Carte par Départements")
st_folium(m_dept, width=700)

# --- Carte régions ---
df_counts_region = df_annuaire.groupby('region_norm').size().reset_index(name='nb_etablissements')
gdf_final_region = gdf_regions.merge(df_counts_region, left_on='nom_norm', right_on='region_norm', how='left')
gdf_final_region['nb_etablissements'] = gdf_final_region['nb_etablissements'].fillna(0)

m_region = folium.Map(location=[46.8, 2.5], zoom_start=5, tiles='cartodbpositron')
folium.Choropleth(
    geo_data=gdf_final_region.__geo_interface__,
    data=gdf_final_region,
    columns=['region', 'nb_etablissements'],
    key_on='feature.properties.region',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Nombre d'établissements"
).add_to(m_region)

folium.GeoJson(
    gdf_final_region,
    name='Régions',
    style_function=lambda x: {'fillOpacity': 0, 'color': 'black', 'weight': 0.5},
    tooltip=folium.GeoJsonTooltip(
        fields=['region', 'nb_etablissements'],
        aliases=['Région', 'Établissements'])
).add_to(m_region)

st.subheader("Carte par Régions")
st_folium(m_region, width=700)