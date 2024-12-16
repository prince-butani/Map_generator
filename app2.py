import streamlit as st
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, ListedColormap
from io import BytesIO

def process_dem(file, palette):
    with rasterio.open(file) as src:
        dem = src.read(1)
        transform = src.transform
        meta = src.meta

    min_elevation, max_elevation = np.min(dem), np.max(dem)

    original_cmap = plt.cm.get_cmap(palette)
    colors = original_cmap(np.linspace(0, 1, 256))
    colors[0] = (1, 1, 1, 1)
    modified_cmap = ListedColormap(colors)

    plt.figure(figsize=(8, 6))
    norm = Normalize(vmin=min_elevation, vmax=max_elevation)
    img = plt.imshow(dem, cmap=modified_cmap, norm=norm)
    cbar = plt.colorbar(img, label='Elevation (meters)', extend='both')
    cbar.set_label('Elevation (meters)', rotation=270, labelpad=20)
    plt.title('Elevation Map')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.xticks(ticks=np.linspace(0, dem.shape[1], num=5), labels=np.round(np.linspace(transform[2], transform[2] + transform[0] * dem.shape[1], num=5), 2))
    plt.yticks(ticks=np.linspace(0, dem.shape[0], num=5), labels=np.round(np.linspace(transform[5], transform[5] + transform[4] * dem.shape[0], num=5), 2))
    plt.gca().set_facecolor('white')

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    classified_file = BytesIO()
    meta.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(classified_file, 'w', **meta) as dst:
        dst.write(dem.astype(rasterio.uint8), 1)

    classified_file.seek(0)
    img_buffer.seek(0)
    return img_buffer, classified_file

st.title("Map Generator")

uploaded_file = st.file_uploader("Upload a DEM file (GeoTIFF format)", type=['tif', 'tiff'])

color_palettes = {
    "Viridis": "viridis",
    "Plasma": "plasma",
    "Inferno": "inferno",
    "Cividis": "cividis",
    "Magma": "magma",
    "Blue_Purple": "PuBu"
}
palette = st.selectbox("Select a color palette", list(color_palettes.keys()))

if uploaded_file is not None:
    st.write("Processing...")
    img, classified_tiff = process_dem(uploaded_file, color_palettes[palette])

    st.image(img, caption="Isarithmic Map", use_column_width=True)

    st.download_button(
        label="Download Elevation Map (PNG)",
        data=img,
        file_name="elevation_map.png",
        mime="image/png"
    )