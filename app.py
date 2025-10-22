import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

st.set_page_config(page_title="Add Scale Bar to Image", layout="centered")
st.title("🧭 Add Scale Bar to Image")

uploaded_file = st.file_uploader("Upload an image (PNG or JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Load image
    img = Image.open(uploaded_file).convert("RGB")
    img_width, img_height = img.size

    st.image(img, caption="Original Image", use_container_width=True)
    st.divider()

    # --- Scale bar controls ---
    st.subheader("Scale Bar Settings")
    scale_length = st.number_input("Scale bar length (µm)", min_value=1, max_value=10000, value=10)
    bar_px = st.number_input("Scale bar width in pixels", min_value=1, max_value=img_width, value=100)
    bar_height = st.slider("Scale bar thickness (px)", 1, 50, 8)

    # Position controls
    x_offset = st.number_input("X position (px from left edge)", min_value=0, max_value=img_width, value=50)
    y_offset = st.number_input("Y position (px from bottom edge)", min_value=0, max_value=img_height, value=50)

    bar_color = st.color_picker("Bar color", "#FFFFFF")
    text_color = st.color_picker("Label color", "#FFFFFF")

    draw = ImageDraw.Draw(img)

    # Convert bottom-based coordinate to image coordinate (top-left origin)
    bar_x = x_offset
    bar_y = img_height - y_offset - bar_height

    # Draw scale bar
    draw.rectangle([(bar_x, bar_y), (bar_x + bar_px, bar_y + bar_height)], fill=bar_color)

    # Label
    font_size = 24
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    text = f"{scale_length} µm"
    text_width, text_height = draw.textsize(text, font=font)
    text_x = bar_x + (bar_px - text_width) / 2
    text_y = bar_y - text_height - 5
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    st.image(img, caption="Image with Scale Bar", use_container_width=True)

    # --- Download modified image ---
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="image_with_scale_bar.png">📥 Download Image with Scale Bar</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("👆 Upload an image above to begin.")
