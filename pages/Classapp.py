import streamlit as st
import qrcode
import pandas as pd
from PIL import Image
from gtts import gTTS
import base64
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(page_title="MK316 Multi-Tool App", layout="wide")

# Streamlit Tabs
tabs = st.tabs(["🏁 QR", "⌚ Timer", "👥 Grouping", "🎧 multi-TTS"])

# QR Code Generator Tab
with tabs[0]:
    st.subheader("QR Code Generator")
    qr_link = st.text_input("Enter a link to generate a QR code:")
    
    generate_qr_button = st.button("Generate QR Code")

    if generate_qr_button and qr_link:
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
        qr_img = qr_img.convert('RGB').resize((300, 300))  # Resize the image
        st.image(qr_img, caption="Generated QR Code", use_column_width=False, width=250)

# Timer Tab (linked to Huggingface)
with tabs[1]:
    st.subheader("⏳ Timer")
    st.write("The timer is linked to the external Huggingface application. Click below to access the timer.")
    
    # Link to the Huggingface timer app
    st.markdown("[Click here to access the Timer on Huggingface](https://huggingface.co/spaces/YOUR_HUGGINGFACE_APP_LINK)")

# Grouping Tool Tab
with tabs[2]:
    st.subheader("👥 Grouping Tool")

    # Upload file section
    uploaded_file = st.file_uploader("Upload CSV File: The file should contain one column labeled 'Names'.", type=["csv"])
    
    # User input for group size
    members_per_group = st.number_input("Members per Group", min_value=1, value=5)
    
    # Input for fixed groups (optional)
    fixed_groups_input = st.text_input("Fixed Groups (separate members by semicolon;)", placeholder="(Optional) format: Name1, Name2; Name3, Name4")

    # Submit button to trigger grouping process
    if st.button("Submit"):
        if uploaded_file is not None:
            def group_names(file, members_per_group, fixed_groups_input):
                # Read the CSV file
                df = pd.read_csv(file)

                # Parse fixed groups input
                fixed_groups = [group.strip() for group in fixed_groups_input.split(';') if group.strip()]
                fixed_groups_df_list = []
                remaining_df = df.copy()

                # Process fixed groups
                for group in fixed_groups:
                    group_names = [name.strip() for name in group.split(',') if name.strip()]
                    matched_rows = remaining_df[remaining_df['Names'].isin(group_names)]
                    fixed_groups_df_list.append(matched_rows)
                    remaining_df = remaining_df[~remaining_df['Names'].isin(group_names)]

                # Shuffle the remaining names
                remaining_df = remaining_df.sample(frac=1).reset_index(drop=True)

                # Add members to fixed groups if they're under the specified group size
                for i, group_df in enumerate(fixed_groups_df_list):
                    while len(group_df) < members_per_group and not remaining_df.empty:
                        group_df = pd.concat([group_df, remaining_df.iloc[[0]]])
                        remaining_df = remaining_df.iloc[1:].reset_index(drop=True)
                    fixed_groups_df_list[i] = group_df

                # Group the remaining names
                groups = fixed_groups_df_list
                for i in range(0, len(remaining_df), members_per_group):
                    groups.append(remaining_df[i:i + members_per_group])

                # Determine the maximum group size
                max_group_size = max(len(group) for group in groups)
                
                # Create DataFrame for grouped data
                grouped_data = {'Group': [f'Group {i+1}' for i in range(len(groups))]}
                for i in range(max_group_size):
                    grouped_data[f'Member{i+1}'] = [group['Names'].tolist()[i] if i < len(group) else "" for group in groups]

                grouped_df = pd.DataFrame(grouped_data)
                return grouped_df

            # Call the group_names function
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

# Multi-Language TTS Tab
with tabs[3]:
    st.subheader("🔊 Text to Speech (Multi-language)")

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
    if st.button("Generate Audio"):
        if text_input.strip() != "":
            mp3_file = text_to_speech(text_input, language)
            st.audio(mp3_file, format="audio/mp3")
        else:
            st.warning("Please enter some text to generate audio.")
