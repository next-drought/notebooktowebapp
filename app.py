import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

# Title of the app
st.title("Vector Data Editor")

# Default file path
default_file_path = "./nyc_roads.geojson"

# Option to choose whether to load the default file or upload a new one
use_default = st.checkbox("Load default file (nyc_roads.geojson)", value=True)

if use_default:
    # Load the vector data from the default file path
    try:
        gdf = gpd.read_file(default_file_path)
    except Exception as e:
        st.error(f"Error reading the default file: {e}")
        st.stop()
else:
    # File uploader for vector data
    uploaded_file = st.file_uploader("Choose a vector file", type=["geojson", "shp"])

    if uploaded_file is not None:
        # Load the vector data (GeoJSON or SHP) into a GeoDataFrame
        try:
            gdf = gpd.read_file(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()
    else:
        st.write("Please upload a vector file to start editing.")
        st.stop()

# Create a Folium map centered on the uploaded/default data
m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=10)

# Add the vector data to the map in an editable form
geo_json = folium.GeoJson(gdf, name="Loaded Data").add_to(m)

# Add the Draw plugin to the map to enable editing
draw = Draw(
    export=True, 
    edit_options={'edit': {'selectedPathOptions': None}},
    draw_options={'polyline': False, 'polygon': True, 'circle': False, 'marker': True}
)
draw.add_to(m)

# Display the map in Streamlit
output = st_folium(m, width=800, height=600)

# Handle the edited data
if output["last_active_drawing"]:
    # Get the last edited drawing from the map
    edited_geojson = output["last_active_drawing"]
    edited_gdf = gpd.GeoDataFrame.from_features(edited_geojson["features"])
    
    # Display the edited GeoDataFrame
    st.write(edited_gdf)

    # Save changes and download the edited data
    if st.button("Save Changes"):
        edited_gdf.to_file("edited_data.geojson", driver="GeoJSON")
        with open("edited_data.geojson", "rb") as file:
            st.download_button("Download Edited File", data=file, file_name="edited_data.geojson")