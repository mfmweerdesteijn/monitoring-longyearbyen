# Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import numpy as np

# Set up our App
st.set_page_config(page_title="Data sweeper", layout="wide")
st.title("Data sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv","xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1]

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file
        st.write(f"**File name:** {file.name}")
        st.write(f"**File size:** {np.round(file.size/1024/1000, decimals=3)} MB")

        # Show 5 rows of our df
        st.write("**Preview head of dataframe**")
        st.dataframe(df.head())

        # Options for data cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1: 
                if st.button(f"Remove duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates removed")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing values filled")
        
        st.dataframe(df.head())           

        # Choose specific columns to keep or convert
        st.subheader("Select columns to convert")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]
        
        # Create some visualizations
        st.subheader("📊 Data visualization")
        if st.checkbox(f"Show visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include=["number"]).iloc[:,:2])

        # Convert the file (CSV <-> Excel)
        st.subheader("Conversion options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV","Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer,index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer,index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)

            # Download button
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file.name,
                mime=mime_type
            )

            st.success("All files processed")