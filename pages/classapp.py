import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pytz
from datetime import datetime

# Function to update the progress circle with time inside or display "Time's Up!"
def update_progress_circle(remaining_time, total_time, time_up):
    fig, ax = plt.subplots(figsize=(3, 3))
    
    if time_up:
        # Show "Time's Up!" in the center of the circle
        ax.pie([1], 
               colors=['#FF9999'], 
               startangle=90, 
               counterclock=False, 
               wedgeprops=dict(width=0.3))
        ax.text(0, 0, "Time's Up!", fontsize=12, va='center', ha='center')  # Display "Time's Up!"
    else:
        # Calculate the proportion of remaining time
        fraction_completed = remaining_time / total_time if total_time > 0 else 0
        ax.pie([fraction_completed, 1 - fraction_completed], 
               colors=['#FF9999', '#D5DEDD'], 
               startangle=90, 
               counterclock=False, 
               wedgeprops=dict(width=0.3))
        
        # Format and add remaining time as text in the center of the circle
        minutes, seconds = divmod(remaining_time, 60)
        ax.text(0, 0, f"{int(minutes):02d}:{int(seconds):02d}", 
                fontsize=24, va='center', ha='center')  # Add remaining time to the center

    ax.set_aspect('equal')
    return fig

# Initialize session state for countdown
if "countdown_started" not in st.session_state:
    st.session_state.countdown_started = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "remaining_time" not in st.session_state:
    st.session_state.remaining_time = 0
if "time_up" not in st.session_state:
    st.session_state.time_up = False

# Title
st.text("👀 MK316 Stopwatch")

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

# Placeholder for the visual circular progress
progress_placeholder = st.empty()

# Timer countdown loop (only runs when countdown has started)
while True:
    # Update the clock every second
    display_current_time()

    if st.session_state.countdown_started and not st.session_state.time_up:
        # Display countdown time while the countdown is running
        if st.session_state.remaining_time >= 0:
            # Update the circular progress chart with time in the center
            fig = update_progress_circle(st.session_state.remaining_time, st.session_state.start_time, time_up=False)
            progress_placeholder.pyplot(fig)

            st.session_state.remaining_time -= 1
            time.sleep(1)
        else:
            # When the countdown finishes, display "Time's Up!" inside the circle and play the sound
            st.session_state.time_up = True
            fig = update_progress_circle(st.session_state.remaining_time, st.session_state.start_time, time_up=True)
            progress_placeholder.pyplot(fig)

            # Play the sound using Streamlit's audio player
            audio_file = open("data/timesup.mp3", "rb")
            st.audio(audio_file.read(), format="audio/mp3")

            st.session_state.countdown_started = False

    # Ensure continuous clock display
    time.sleep(0.1)
