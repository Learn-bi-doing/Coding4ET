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
    st.subheader("QR Code Generator")
    
    # Web address input
    qr_link = st.text_input("Enter a link to generate a QR code:")
    
    # Additional information input
    additional_info = st.text_input("Enter additional information to include in the QR code:")

    # Add a Submit button
    generate_qr_button = st.button(additional_info)

    if generate_qr_button and qr_link:
        # Combine the web address and additional info to generate the QR code
        full_text = f"{qr_link}\n{additional_info}" if additional_info else qr_link
        
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_text)  # Use the combined text
        qr.make(fit=True)

        qr_img = qr.make_image(fill='black', back_color='white')

        # Convert the QR code image to RGB format and resize
        qr_img = qr_img.convert('RGB')  # Convert to RGB to be compatible with st.image
        qr_img = qr_img.resize((300, 300))  # Resize the image

        # Save the image as a temporary file
        qr_img.save("qr_code_resized.png")

        # Display the resized image using Streamlit
        st.image("qr_code_resized.png", caption="Generated QR Code", use_column_width=False, width=250)

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
