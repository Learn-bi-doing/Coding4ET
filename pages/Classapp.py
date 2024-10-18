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

# Streamlit tabs
tabs = st.tabs(["🏁 QR", "⌚ Timer", "👥 Grouping", "🎧 multi-TTS"])

# Timer tab
# Timer tab (using Hugging Face deployment)
with tabs[1]:
    st.subheader("Timer from Hugging Face")
    # Embed Hugging Face Timer using an iframe
    hf_timer_url = "https://huggingface.co/spaces/MK-316/mytimer"  # Replace with your actual Hugging Face URL
    components.html(f"""
        <iframe width="800" height="600" src="{hf_timer_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    """, height=600)

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
