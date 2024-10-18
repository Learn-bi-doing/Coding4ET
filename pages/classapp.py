import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
import pytz
from datetime import datetime

# Function to update the progress circle with time inside or display "Time's Up!"
def update_progress_circle(remaining_time, total_time, time_up):
    fig, ax = plt.subplots(figsize=(2, 2))  # Smaller figure size to fit layout
    
    if time_up:
        # Show "Time's Up!" in the center of the circle
        ax.pie([1], 
               colors=['#6d8c9c'], 
               startangle=90, 
               counterclock=False, 
               wedgeprops=dict(width=0.3))
        ax.text(0, 0, "Time's Up!", fontsize=10, va='center', ha='center')  # Smaller font size for "Time's Up!"
    else:
        # Calculate the proportion of remaining time
        fraction_completed = remaining_time / total_time if total_time > 0 else 0
        ax.pie([fraction_completed, 1 - fraction_completed], 
               colors=['#6d8c9c', '#D5DEDD'], 
               startangle=90, 
               counterclock=False, 
               wedgeprops=dict(width=0.3))
        
        # Format and add remaining time as text in the center of the circle
        minutes, seconds = divmod(remaining_time, 60)
        ax.text(0, 0, f"{int(minutes):02d}:{int(seconds):02d}", 
                fontsize=14, va='center', ha='center')  # Adjusted font size for remaining time

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
st.text("👀 MK316 Timer with Circular Progress")

# Placeholder to display the current time (digital clock)
current_time_placeholder = st.empty()

# Function to display the current time (as a live digital clock)
def display_current_time():
    seoul_tz = pytz.timezone('Asia/Seoul')  # Set timezone to Seoul
    current_time = datetime.now(seoul_tz).strftime("%H:%M:%S")  # Convert to Seoul time

    # Style the clock (increase font size and set color)
    current_time_placeholder.markdown(
        f"<h1 style='text-align: center; font-size: 60px; color: #5785A4;'>{current_time}</h1>",  # Smaller clock font size
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

# Set up the layout in two columns
col1, col2 = st.columns([1, 1])

# Left column: Input field, buttons, and audio
with col1:
    # Input field for countdown time in seconds
    st.session_state.start_time = st.number_input("Time (s)", min_value=0, max_value=3600, value=10, label_visibility="visible")
    
    # Add custom button colors using Streamlit's CSS support
    st.markdown("""
        <style>
        div.stButton > button {
            width: 8em;
            height: 2.5em;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Start and Reset buttons
    start_button, reset_button = st.columns([1, 1])
    
    with start_button:
        if st.button("Start"):
            start_countdown()
    
    with reset_button:
        if st.button("Reset"):
            reset_countdown()

    # Audio player placeholder, shown after countdown finishes
    audio_placeholder = st.empty()

# Right column: Circular progress chart
with col2:
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
            # When the countdown finishes, display "Time's Up!" inside the circle
            st.session_state.time_up = True
            fig = update_progress_circle(st.session_state.remaining_time, st.session_state.start_time, time_up=True)
            progress_placeholder.pyplot(fig)

            # Play the sound using Streamlit's audio player in the left column
            with col1:
                audio_file = open("data/timesup.mp3", "rb")
                audio_placeholder.audio(audio_file.read(), format="audio/mp3")

            st.session_state.countdown_started = False

    # Ensure continuous clock display
    time.sleep(0.1)
