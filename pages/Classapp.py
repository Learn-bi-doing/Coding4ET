import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import time
import pytz
from datetime import datetime
from gtts import gTTS

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

# Streamlit tabs
tabs = st.tabs(["🏁 QR", "⌚ Timer", "👥 Grouping", "🎧 multi-TTS"])

# Timer tab
with tabs[1]:
    st.text("👀 MK316 Timer")

    # Initialize session state for countdown
    if "countdown_started" not in st.session_state:
        st.session_state.countdown_started = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = 0
    if "remaining_time" not in st.session_state:
        st.session_state.remaining_time = 0
    if "time_up" not in st.session_state:
        st.session_state.time_up = False

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
        st_autorefresh(interval=0, limit=1)  # Trigger a refresh

    # Set up the layout in two columns
    col1, col2 = st.columns([1, 1])

    # Left column: Current time, input field, buttons, and audio
    with col1:
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

    # Timer countdown logic (continuously updates)
    if st.session_state.countdown_started and not st.session_state.time_up:
        if st.session_state.remaining_time > 0:
            # Update the circular progress chart with time in the center
            fig = update_progress_circle(st.session_state.remaining_time, st.session_state.start_time, time_up=False)
            progress_placeholder.pyplot(fig)

            # Decrease the remaining time
            st.session_state.remaining_time -= 1

            # Refresh the app after 1 second
            st.experimental_rerun()
        else:
            # When the countdown finishes, display "Time's Up!" inside the circle
            st.session_state.time_up = True
            fig = update_progress_circle(st.session_state.remaining_time, st.session_state.start_time, time_up=True)
            progress_placeholder.pyplot(fig)

            # Play the sound using Streamlit's audio player
            with col1:
                audio_file = open("data/timesup.mp3", "rb")
                audio_placeholder.audio(audio_file.read(), format="audio/mp3")

    # Autorefresh the app every 1 second to update the clock
    display_current_time()
    st_autorefresh(interval=1000, limit=1000)

# Grouping tab
with tabs[2]:
    st.subheader("👥 Grouping Tool")

    # Upload file section
    uploaded_file = st.file_uploader("Upload CSV File: Note that there should be only one column with 'Names' as column name.", type=["csv"])
    
    # User input for group size
    members_per_group = st.number_input("Members per Group", min_value=1, value=5)
    
    # Input for fixed groups (optional)
    fixed_groups_input = st.text_input("Fixed Groups (if more than two fixed members, separate them by semicolon;)", placeholder="(Optional) format: Name1, Name2; Name3, Name4")

    # Submit button to trigger grouping process
    if st.button("Submit"):
        if uploaded_file is not None:
            # Function to group names
            def group_names(file, members_per_group, fixed_groups_input):
                # Read the CSV file
                df = pd.read_csv(file)

                # Parse fixed groups input
                fixed_groups = [group.strip() for group in fixed_groups_input.split(';') if group.strip()]
                fixed_groups_df_list = []
                remaining_df = df.copy()

                # Process fixed groups and create a list for additional members to be added
                for group in fixed_groups:
                    group_names = [name.strip() for name in group.split(',') if name.strip()]
                    # Find these names in the DataFrame
                    matched_rows = remaining_df[remaining_df['Names'].isin(group_names)]
                    fixed_groups_df_list.append(matched_rows)
                    # Remove these names from the pool of remaining names
                    remaining_df = remaining_df[~remaining_df['Names'].isin(group_names)]

                # Shuffle the remaining DataFrame
                remaining_df = remaining_df.sample(frac=1).reset_index(drop=True)
                
                # Adjusting fixed groups to include additional members if they're under the specified group size
                for i, group_df in enumerate(fixed_groups_df_list):
                    while len(group_df) < members_per_group and not remaining_df.empty:
                        group_df = pd.concat([group_df, remaining_df.iloc[[0]]])
                        remaining_df = remaining_df.iloc[1:].reset_index(drop=True)
                    fixed_groups_df_list[i] = group_df  # Update the group with added members

                # Grouping the remaining names
                groups = fixed_groups_df_list  # Start with adjusted fixed groups
                for i in range(0, len(remaining_df), members_per_group):
                    groups.append(remaining_df[i:i + members_per_group])

                # Determine the maximum group size
                max_group_size = max(len(group) for group in groups)
                
                # Creating a new DataFrame for grouped data with separate columns for each member
                grouped_data = {'Group': [f'Group {i+1}' for i in range(len(groups))]}
                # Add columns for each member
                for i in range(max_group_size):
                    grouped_data[f'Member{i+1}'] = [group['Names'].tolist()[i] if i < len(group) else "" for group in groups]

                grouped_df = pd.DataFrame(grouped_data)
                
                return grouped_df

            # Call the group_names function and display the grouped names
            grouped_df = group_names(uploaded_file, members_per_group, fixed_groups_input)
            
            # Display the grouped names
            st.write(grouped_df)
            
            # Option to download the grouped names as CSV
            csv = grouped_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Grouped Names as CSV",
                data=csv,
                file_name='grouped_names.csv',
                mime='text/csv',
            )

        else:
            st.error("Please upload a CSV file before submitting.")

# Text-to-Speech tab
with tabs[3]:
    st.subheader("🔊 Text to Speech Application (Multi-languages)")

    # Text input for TTS
    text_input = st.text_area("Enter text here:", "")
    
    # Language selection
    language = st.selectbox("Choose language:", ["🇰🇷 Korean", "🇺🇸 English (AmE)", "🇬🇧 English (BrE)", "🇫🇷 French", "🇪🇸 Spanish", "🇨🇳 Chinese"])

    # Function to handle TTS
    def text_to_speech(text, language):
        language_map = {
            "🇰🇷 Korean": "ko",
            "🇺🇸 English (AmE)": ("en", "us"),
            "🇬🇧 English (BrE)": ("en", "co.uk"),
            "🇫🇷 French": "fr",
            "🇪🇸 Spanish": ("es", "es"),
            "🇨🇳 Chinese": "zh-CN"
        }

        if isinstance(language_map[language], tuple):
            lang, tld = language_map[language]
            tts = gTTS(text=text, lang=lang, tld=tld)
        else:
            lang = language_map[language]
            tts = gTTS(text=text, lang=lang)

        tts.save("output.mp3")
        return "output.mp3"
    
    # Button to generate speech
    if st.button("Text-To-speech"):
        if text_input.strip() != "":
            mp3_file = text_to_speech(text_input, language)
            st.audio(mp3_file, format="audio/mp3")
        else:
            st.warning("Please enter some text to generate audio.")
