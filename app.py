import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV + Data Dictionary Upload", layout="centered")

st.title("📊 Upload Dataset and Optional Data Dictionary")

# 1. Upload CSV Dataset (Required)
st.header("📁 Upload CSV Dataset (Required)")
uploaded_csv = st.file_uploader("Upload your main dataset (CSV format)", type=["csv"], key="dataset")

# 2. Upload Data Dictionary (Optional)
st.header("📑 Upload Data Dictionary (Optional)")
uploaded_dict = st.file_uploader("Upload your data dictionary (CSV or Excel)", type=["csv", "xlsx"], key="dictionary")

# เมื่อผู้ใช้ upload dataset แล้ว
if uploaded_csv is not None:
    df = pd.read_csv(uploaded_csv)
    st.subheader("✅ Dataset Preview")
    st.dataframe(df.head())

    # ตรวจสอบว่ามี Data Dictionary มั้ย
    if uploaded_dict is not None:
        st.success("✅ Using uploaded data dictionary.")
        try:
            if uploaded_dict.name.endswith(".csv"):
                data_dict = pd.read_csv(uploaded_dict)
            else:
                data_dict = pd.read_excel(uploaded_dict)
            st.subheader("📖 Uploaded Data Dictionary")
            st.dataframe(data_dict)
        except Exception as e:
            st.error(f"❌ Error reading data dictionary: {e}")
    else:
        st.warning("⚠️ No Data Dictionary uploaded. Generating one with AI...")
        
        # 🔍 สร้าง Data Dictionary แบบง่ายจากข้อมูล df
        def generate_data_dictionary(df):
            dict_entries = []
            for col in df.columns:
                entry = {
                    "Column Name": col,
                    "Data Type": str(df[col].dtype),
                    "Example Value": df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A",
                    "Description": "Auto-generated description (to be filled)"
                }
                dict_entries.append(entry)
            return pd.DataFrame(dict_entries)

        generated_dict = generate_data_dictionary(df)
        st.subheader("🤖 Auto-Generated Data Dictionary")
        st.dataframe(generated_dict)

else:
    st.info("Please upload a CSV dataset to proceed.")
