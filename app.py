import streamlit as st
import pandas as pd

st.set_page_config(page_title="Upload Dataset + Dictionary", layout="wide")
st.title("🧠 CSV Chatbot Assistant with Optional Data Dictionary")

# Tabs: แยกเป็น 2 หน้าชัดเจน
tab1, tab2 = st.tabs(["📁 Upload CSV Dataset", "📑 Upload Data Dictionary"])

# -------------------- TAB 1: Upload CSV Dataset -------------------- #
with tab1:
    st.header("📁 Upload CSV Dataset (Required)")
    uploaded_csv = st.file_uploader("Upload your main dataset (.csv)", type=["csv"], key="csv_upload")

    if uploaded_csv is not None:
        df = pd.read_csv(uploaded_csv)
        st.success("✅ Dataset uploaded successfully!")
        st.subheader("📊 Preview of Dataset")
        st.dataframe(df.head())
    else:
        st.info("Please upload your main CSV dataset to proceed.")

# -------------------- TAB 2: Upload Data Dictionary -------------------- #
with tab2:
    st.header("📑 Upload Data Dictionary (Optional)")
    uploaded_dict = st.file_uploader("Upload a data dictionary (.csv or .xlsx)", type=["csv", "xlsx"], key="dict_upload")

    # ถ้า user ไม่ได้อัปโหลด dictionary แต่มี dataset แล้ว → ให้สร้างอัตโนมัติ
    if uploaded_dict is not None:
        st.success("✅ Data Dictionary uploaded!")
        try:
            if uploaded_dict.name.endswith(".csv"):
                data_dict = pd.read_csv(uploaded_dict)
            else:
                data_dict = pd.read_excel(uploaded_dict)
            st.subheader("📖 Uploaded Data Dictionary")
            st.dataframe(data_dict)
        except Exception as e:
            st.error(f"❌ Error reading data dictionary: {e}")
    elif "df" in locals():
        st.warning("⚠️ No Data Dictionary uploaded. Generating one with AI...")

        def generate_data_dictionary(df):
            dict_entries = []
            for col in df.columns:
                entry = {
                    "Column Name": col,
                    "Data Type": str(df[col].dtype),
                    "Example Value": df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A",
                    "Description": "Auto-generated description (can be edited)"
                }
                dict_entries.append(entry)
            return pd.DataFrame(dict_entries)

        generated_dict = generate_data_dictionary(df)
        st.subheader("🤖 Auto-Generated Data Dictionary")
        st.dataframe(generated_dict)
    else:
        st.info("Please upload a CSV dataset first in the first tab.")
