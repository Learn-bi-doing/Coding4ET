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
import pandas as pd

# Streamlit tabs
tabs = st.tabs(["📈 QR", "⏳ Timer", "👥 Group Names", "🎬 Videos"])

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


# Timer tab (Tab 2)
with tabs[1]:
    st.subheader("⏳ MK316 Timer with Circular Progress")

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

# Grouping tab (Tab 3)
with tabs[2]:
    st.subheader("Group Names")
    
    # Upload CSV
    uploaded_file = st.file_uploader("Upload CSV with 'Names' column", type=['csv'])

    # Group size input
    members_per_group = st.number_input("Members per Group", value=5)

    # Textbox for fixed groups input
    fixed_groups_input = st.text_area("Fixed Groups (Optional)", 
                                      placeholder="Name1, Name2; Name3, Name4")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        st.write("Preview of Uploaded Data:", df)

        # Function to group names
        def group_names(df, members_per_group, fixed_groups_input):
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

        # Generate groups
        if st.button("Generate Groups"):
            grouped_df = group_names(df, members_per_group, fixed_groups_input)
            st.write("Generated Groups:", grouped_df)

            # Provide download option for grouped names
            grouped_csv = grouped_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("Download Grouped Names as CSV", data=grouped_csv, file_name="grouped_names.csv")

# Video embedding tab (Tab 4)
with tabs[3]:
    st.subheader("Tutorials")
    st.write("Below is an embedded video from YouTube: Coding basics")
    # Embed YouTube video using HTML iframe
    html_code = """
    <iframe width="500" height="400" src="https://www.youtube.com/embed/uigxMFBR0Wg" 
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; 
    gyroscope; picture-in-picture" allowfullscreen></iframe>
    """
    components.html(html_code, height=500)

