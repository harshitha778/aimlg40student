import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Student Enrollment Analytics",
    layout="wide"
)

st.title("🎓 Student Enrollment Analytics Dashboard")
st.write("Welcome to the Student Enrollment Analytics project!")

# Load dataset
df = pd.read_csv("data/enrollment_data.csv")

st.subheader("Dataset Preview")
st.dataframe(df)

st.subheader("Enrollment by Course")
st.bar_chart(df["Course"].value_counts())