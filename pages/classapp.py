import streamlit as st
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import qrcode
from PIL import Image

# Creating the word cloud
def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud

# Streamlit tabs
tabs = st.tabs(["📈 QR", "🗃 Data", "🌌 Word Cloud", "🎬 Videos"])

# QR Code tab
with tabs[0]:
    st.subheader("Generate QR Code")
    
    # User input for the link
    user_link = st.text_input("Enter a URL or text to generate a QR code:")
    
    # Generate QR code when the user submits a valid link or text
    if st.button("Generate QR Code") and user_link:
        qr_img = qrcode.make(user_link)  # Generate QR code image
        img_path = "qrcode_image.png"
        qr_img.save(img_path)  # Save the image temporarily
        
        # Display the QR code image on the same page
        st.image(img_path, caption="Here is your QR code:", width=300, height=300, use_column_width=True)

# Data tab
with tabs[1]:
    st.subheader("A tab with the data")
    data = np.random.randn(10, 1)  # Random data for display
    st.write(data)

# Word cloud tab
with tabs[2]:
    st.subheader("A tab with a word cloud")
    st.markdown("Please enter some text to generate a word cloud. [sample text](https://raw.githubusercontent.com/MK316/MK-316/refs/heads/main/data/sampletext.txt)")
    user_input = st.text_input("Enter text to create a word cloud:")
    generate_button = st.button("Generate Word Cloud")

    if generate_button and user_input:  # Generate only when the button is clicked
        wordcloud = create_wordcloud(user_input)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

# Video embedding tab
with tabs[3]:
    st.subheader("Tutorials")
    st.write("Below is an embedded video from YouTube: Coding basics")
    # Embed YouTube video using HTML iframe
    html_code = """
    <iframe width="500" height="400" src="https://www.youtube.com/embed/uigxMFBR0Wg" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    """
    components.html(html_code, height=500)
