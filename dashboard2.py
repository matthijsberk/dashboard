import streamlit as st
import pandas as pd
import plotly.express as px

# Load the Excel file
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)  # Read the uploaded Excel file
    df['Class Date'] = pd.to_datetime(df['Class Date'], errors='coerce')  # Convert 'Class Date' to datetime
    df = df.dropna(subset=['Class Date'])  # Remove rows with invalid dates
    return df

# Streamlit file uploader
st.sidebar.header("Upload File")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    # Add a column for the day of the week (0=Monday, 6=Sunday)
    data['Day of Week'] = data['Class Date'].dt.weekday  # Extract weekday from 'Class Date'

    # Streamlit filter for section selection
    section_ids = data['Section ID'].unique()  # Get unique section IDs
    selected_section = st.sidebar.selectbox("Select Section ID", section_ids)  # Select section ID from sidebar

    # Filter data based on selected section ID
    section_data = data[data['Section ID'] == selected_section]

    # Overview of all students (Horizontal Stacked Bar Chart)
    verplicht_data = section_data.copy()  # Use filtered dataset for the stacked bar chart
    verplicht_data['Attendance'] = verplicht_data['Attendance'].map({'present': 1, 'late': 1, 'absent': 0}).fillna(0)  # Map attendance to numerical values

    # Summarize attendance data for each student
    student_summary = verplicht_data.groupby('Student Name')['Attendance'].agg(['sum', 'count']).reset_index()
    student_summary['Percentage Present/Late'] = (student_summary['sum'] / student_summary['count']) * 100  # Calculate percentage present/late

    # Sorting option for stacked bar chart
    sort_option = st.sidebar.selectbox("Sort Stacked Bar Chart By", ['Percentage', 'Name'])
    
    # Sort student data based on selected option
    if sort_option == 'Percentage':
        student_summary = student_summary.sort_values(by='Percentage Present/Late', ascending=False)
    else:
        student_summary = student_summary.sort_values(by='Student Name', ascending=True)

    # Create a horizontal stacked bar chart to show attendance percentage
    stacked_bar_fig = px.bar(
        student_summary,
        y='Student Name',
        x='Percentage Present/Late',
        orientation='h',
        title=f'Total Percentage of Present/Late for Section {selected_section}',
        labels={'Percentage Present/Late': 'Attendance Percentage', 'Student Name': 'Student'},
        text='Student Name'  # Display student name on the bar
    )

    # Customize layout for better readability
    stacked_bar_fig.update_layout(
        yaxis_title='Student Name',
        xaxis_title='Attendance Percentage',
        height=800,  # Increase height to fit all student names next to the bars
        margin=dict(l=200)  # Increase left margin to ensure all names are visible
    )

    # Show the stacked bar chart
    st.plotly_chart(stacked_bar_fig, use_container_width=True, key='stacked_bar_chart')
else:
    st.write("Please upload an Excel file to proceed.")