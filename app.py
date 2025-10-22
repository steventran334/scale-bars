import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- Example image or plot dimensions (in pixels) ---
image_width, image_height = 800, 600

st.subheader("Scale Bar Settings")
scale_length = st.number_input("Scale bar length (µm)", min_value=1, max_value=1000, value=10)
x_offset = st.number_input("X position (px from left)", min_value=0, max_value=image_width, value=50, step=1)
y_offset = st.number_input("Y position (px from bottom)", min_value=0, max_value=image_height, value=50, step=1)

# --- Create figure ---
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, image_width)
ax.set_ylim(0, image_height)
ax.set_facecolor("black")

# --- Draw scale bar ---
scale_bar_width = 100  # in pixels, for visual example
rect = patches.Rectangle(
    (x_offset, y_offset), scale_bar_width, 5, color="white"
)
ax.add_patch(rect)

# --- Label (optional) ---
ax.text(x_offset + scale_bar_width / 2, y_offset + 15, f"{scale_length} µm",
        color="white", ha="center", va="bottom", fontsize=12)

ax.invert_yaxis()  # if working in image coordinate space
st.pyplot(fig)
