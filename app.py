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
                sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"
                dtype = df[col].dtype

                # ตรวจจับประเภทข้อมูลโดยละเอียด
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    inferred_type = "date"
                elif pd.api.types.is_integer_dtype(df[col]):
                    inferred_type = "int64"
                elif pd.api.types.is_float_dtype(df[col]):
                    inferred_type = "float64"
                elif pd.api.types.is_bool_dtype(df[col]):
                    inferred_type = "bool"
                elif pd.api.types.is_string_dtype(df[col]) or dtype == "object":
                    try:
                        # พยายามแปลงเป็นวันที่เพื่อดูว่าใช่ date หรือไม่
                        parsed = pd.to_datetime(df[col], errors="coerce")
                        if parsed.notna().sum() > 0:
                            inferred_type = "date"
                        else:
                            inferred_type = "string"
                    except:
                        inferred_type = "string"
                else:
                    inferred_type = str(dtype)

                dict_entries.append({
                    "Column Name": col,
                    "Data Type": inferred_type,
                    "Example Value": sample_value"
                })

            return pd.DataFrame(dict_entries)

        generated_dict = generate_data_dictionary(df)
        st.subheader("🤖 Auto-Generated Data Dictionary")
        st.dataframe(generated_dict)
    else:
        st.info("Please upload a CSV dataset first in the first tab.")
