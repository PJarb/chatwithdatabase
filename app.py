import streamlit as st
import pandas as pd
import google.generativeai as genai

# โหลด Gemini API Key
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyBdf4nh_jx7Jq3M8lZ4Zbfim6GULaNr9iI")  # แก้ใส่ตรง ๆ ได้
genai.configure(api_key=GEMINI_API_KEY)

# ---------- ฟังก์ชันวิเคราะห์ column ด้วย Gemini ---------- #
def generate_gemini_descriptions(df: pd.DataFrame) -> list:
    model = genai.GenerativeModel("gemini-pro")
    descriptions = []

    for col in df.columns:
        sample_values = df[col].dropna().astype(str).unique()[:5]
        prompt = f"""
You are a data analyst. Analyze the following column and provide a clear, concise description of what it likely represents.

Column name: {col}
Sample values: {', '.join(sample_values)}

Respond with just the description in one sentence.
"""
        try:
            response = model.generate_content(prompt)
            descriptions.append(response.text.strip())
        except Exception as e:
            descriptions.append(f"(Error generating description: {e})")

    return descriptions

# ---------- ฟังก์ชันวิเคราะห์ประเภทข้อมูล ---------- #
def infer_column_type(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    elif pd.api.types.is_integer_dtype(series):
        return "int64"
    elif pd.api.types.is_float_dtype(series):
        return "float64"
    elif pd.api.types.is_bool_dtype(series):
        return "bool"
    elif pd.api.types.is_string_dtype(series) or series.dtype == "object":
        try:
            parsed = pd.to_datetime(series, errors="coerce")
            if parsed.notna().sum() > 0:
                return "date"
            else:
                return "string"
        except:
            return "string"
    else:
        return str(series.dtype)

# ---------- เริ่มต้น Streamlit App ---------- #
st.set_page_config(page_title="CSV + Data Dictionary with Gemini", layout="wide")
st.title("🧠 CSV Chatbot Assistant with Optional Data Dictionary (Gemini AI)")

tab1, tab2 = st.tabs(["📁 Upload CSV Dataset", "📑 Upload Data Dictionary"])

# -------------------- TAB 1: Upload CSV Dataset -------------------- #
with tab1:
    st.header("📁 Upload CSV Dataset (Required)")
    uploaded_csv = st.file_uploader("Upload your main dataset (.csv)", type=["csv"])

    if uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        st.success("✅ Dataset uploaded successfully!")
        st.subheader("🔍 Preview of Dataset")
        st.dataframe(df.head())
    else:
        st.info("Please upload your main CSV dataset to proceed.")

# -------------------- TAB 2: Upload or Generate Data Dictionary -------------------- #
with tab2:
    st.header("📑 Upload Data Dictionary (Optional)")
    uploaded_dict = st.file_uploader("Upload a data dictionary (.csv or .xlsx)", type=["csv", "xlsx"])

    if uploaded_dict:
        try:
            if uploaded_dict.name.endswith(".csv"):
                data_dict = pd.read_csv(uploaded_dict)
            else:
                data_dict = pd.read_excel(uploaded_dict)
            st.success("✅ Data Dictionary uploaded.")
            st.subheader("📖 Uploaded Data Dictionary")
            st.dataframe(data_dict)
        except Exception as e:
            st.error(f"❌ Error reading dictionary: {e}")

    elif 'df' in locals():
        st.warning("⚠️ No Data Dictionary uploaded. Generating one with Gemini AI...")

        # Generate types and descriptions
        types = [infer_column_type(df[col]) for col in df.columns]
        examples = [df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A" for col in df.columns]
        descriptions = generate_gemini_descriptions(df)

        data_dict = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": types,
            "Example Value": examples,
            "Description": descriptions
        })

        st.subheader("🤖 Gemini-Generated Data Dictionary")
        st.dataframe(data_dict)
    else:
        st.info("Please upload a dataset first in the first tab.")
