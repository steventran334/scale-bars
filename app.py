import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- SCALE MAP ---
PIXELS_PER_MICRON = {
    "5x": 0.255,
    "10x": 0.515,
    "20x": 1.0325,
    "40x": 2.0425,
    "63x": 3.27,
    "100x": 5.16
}

st.title("🔬 Microscope Image Scale Bar Adder")

st.markdown("""
Upload one or more microscope images, choose the magnification,
and automatically add a scale bar to each image.
""")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Settings")
magnification = st.sidebar.selectbox("Select magnification", list(PIXELS_PER_MICRON.keys()))
scale_length_um = st.sidebar.number_input("Scale bar length (µm)", min_value=5, max_value=200, value=50)
bar_height_px = st.sidebar.number_input("Scale bar thickness (pixels)", min_value=2, max_value=50, value=8)
margin_px = st.sidebar.number_input("Margin from edges (pixels)", min_value=5, max_value=200, value=50)

# --- FILE UPLOAD ---
uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png", "tif", "tiff"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"### {len(uploaded_files)} file(s) uploaded")

    annotated_images = []

    for uploaded_file in uploaded_files:
        # Load image
        img = Image.open(uploaded_file).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Scale calculation
        px_per_um = PIXELS_PER_MICRON[magnification]
        bar_length_px = int(px_per_um * scale_length_um)

        # Image dimensions
        w, h = img.size

        # Coordinates for the scale bar (bottom-right)
        x1 = w - margin_px - bar_length_px
        y1 = h - margin_px - bar_height_px
        x2 = w - margin_px
        y2 = h - margin_px

        # Draw scale bar
        draw.rectangle([x1, y1, x2, y2], fill="white")

        # Optional label
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        text = f"{scale_length_um} µm"
        tw, th = draw.textsize(text, font=font)
        draw.text((x1 + (bar_length_px - tw) / 2, y1 - th - 5), text, fill="white", font=font)

        # Save annotated image to memory
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        annotated_images.append((uploaded_file.name, buf))

        st.image(img, caption=f"{uploaded_file.name} ({magnification}, {scale_length_um} µm bar)", use_column_width=True)
        st.download_button(
            label=f"⬇️ Download {uploaded_file.name}",
            data=buf,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_scalebar.jpg",
            mime="image/jpeg"
        )

    # --- BULK DOWNLOAD ZIP ---
    if len(annotated_images) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, buf in annotated_images:
                zipf.writestr(f"{os.path.splitext(name)[0]}_scalebar.jpg", buf.getvalue())
        zip_buffer.seek(0)

        st.download_button(
            label="⬇️ Download All as ZIP",
            data=zip_buffer,
            file_name="annotated_images.zip",
            mime="application/zip"
        )
