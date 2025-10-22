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
scale_length_um = st.sidebar.number_input("Scale bar length (µm)", min_value=1, max_value=200, value=50)
bar_height_px = st.sidebar.number_input("Scale bar thickness (pixels)", min_value=1, max_value=50, value=8)

# --- POSITIONING MODE ---
position_mode = st.sidebar.radio(
    "Scale bar positioning mode:",
    ("Margin from bottom-right", "Manual X/Y position")
)

if position_mode == "Margin from bottom-right":
    margin_px = st.sidebar.number_input("Margin from edges (pixels)", min_value=1, max_value=1000, value=50)
else:
    st.sidebar.markdown("#### Manual X/Y offset (from top-left corner)")
    x_offset = st.sidebar.number_input("X offset (pixels)", min_value=0, max_value=5000, value=50)
    y_offset = st.sidebar.number_input("Y offset (pixels)", min_value=0, max_value=5000, value=50)

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
        w, h = img.size

        # --- Determine coordinates based on mode ---
        if position_mode == "Margin from bottom-right":
            x1 = w - margin_px - bar_length_px
            y1 = h - margin_px - bar_height_px
        else:  # Manual X/Y
            x1 = x_offset
            y1 = y_offset

        x2 = x1 + bar_length_px
        y2 = y1 + bar_height_px

        # Draw scale bar
        draw.rectangle([x1, y1, x2, y2], fill="white")

        # Label (Unicode-safe)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()

        text = f"{scale_length_um} µm"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        draw.text((x1 + (bar_length_px - tw) / 2, y1 - th - 5), text, fill="white", font=font)

        # Save annotated image
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
