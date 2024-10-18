import streamlit as st
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import qrcode
from PIL import Image
import time
import pytz
from datetime import datetime

# Creating the word cloud
def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud

# Streamlit tabs
tabs = st.tabs(["📈 QR", "⏳ Timer", "🌌 Word Cloud", "🎬 Videos"])

# QR Code tab
with tabs[0]:
    st.subheader("QR Code Generator")
    qr_link = st.text_input("Enter a link to generate a QR code:")

    if qr_link:
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_link)
        qr.make(fit=True)

        qr_img = qr.make_image(fill='black', back_color='white')

        # Convert the QR code image to RGB format and resize
        qr_img = qr_img.convert('RGB')  # Convert to RGB to be compatible with st.image
        qr_img = qr_img.resize((300, 300))  # Resize the image

        # Save the image as a temporary file
        qr_img.save("qr_code_resized.png")

        # Display the resized image using Streamlit
        st.image("qr_code_resized.png", caption="Generated QR Code", use_column_width=False, width=250)

# Timer tab
with tabs[1]:
    st.subheader("MK316 Quiet Timer ⏳")

    # Initialize session state for countdown
    if "countdown_started" not in st.session_state:
        st.session_state.countdown_started = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = 0
    if "remaining_time" not in st.session_state:
        st.session_state.remaining_time = 0
    if "time_up" not in st.session_state:
        st.session_state.time_up = False

    # Placeholder to display the current time (digital clock)
    current_time_placeholder = st.empty()

    # Function to display the current time (as a live digital clock)
    def display_current_time():
        seoul_tz = pytz.timezone('Asia/Seoul')  # Set timezone to Seoul
        current_time = datetime.now(seoul_tz).strftime("%H:%M:%S")  # Convert to Seoul time

        # Style the clock (increase font size and set color)
        current_time_placeholder.markdown(
            f"<h1 style='text-align: center; font-size: 80px; color: #5785A4;'>{current_time}</h1>",  # Large font
            unsafe_allow_html=True
        )

    # Function to start the countdown timer
    def start_countdown():
        if not st.session_state.countdown_started:
            st.session_state.remaining_time = st.session_state.start_time
            st.session_state.countdown_started = True
            st.session_state.time_up = False

    # Function to reset the countdown timer
    def reset_countdown():
        st.session_state.start_time = 0
        st.session_state.remaining_time = 0
        st.session_state.countdown_started = False
        st.session_state.time_up = False

    # Input field for countdown time in seconds
    st.session_state.start_time = st.number_input("Set Countdown Time (in seconds)", min_value=0, max_value=3600, value=10)

    # Add custom button colors using Streamlit's CSS support
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #D5DEDD;
            color: black;
            height: 3em;
            width: 10em;
            border-radius: 10px;
            border: 2px solid #9EA8A7;
            font-size: 20px;
            font-weight: bold;
        }
    
        div.stButton > button:last-child {
            background-color: #B2E8E2;
            color: black;
            height: 3em;
            width: 10em;
            border-radius: 10px;
            border: 2px solid #13645B;
            font-size: 20px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Countdown Start, Stop, and Reset buttons aligned in two columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Countdown"):
            start_countdown()
    with col2:
        if st.button("Reset Countdown"):
            reset_countdown()

    # Placeholder for displaying the countdown time
    countdown_placeholder = st.empty()

    # Timer countdown loop (only runs when countdown has started)
    while True:
        # Update the clock every second
        display_current_time()

        if st.session_state.countdown_started and not st.session_state.time_up:
            # Display countdown time while the countdown is running
            if st.session_state.remaining_time > 0:
                minutes, seconds = divmod(st.session_state.remaining_time, 60)
                countdown_placeholder.write(f"**Remaining Time:** {int(minutes):02d}:{int(seconds):02d}")
                st.session_state.remaining_time -= 1
            else:
                # When the countdown finishes, display the message and play the sound
                st.session_state.time_up = True
                countdown_placeholder.write("⏰ **Time's Up!**")
                st.session_state.countdown_started = False

                # Play the sound using Streamlit's audio player
                audio_file = open("/data/timesup.mp3", "rb")
                st.audio(audio_file.read(), format="audio/mp3")

        # Sleep for a second
        time.sleep(1)

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
