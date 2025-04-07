import streamlit as st
import pandas as pd
import numpy as np

from typing import List

st.set_page_config(page_title="Upload Dataset + Dictionary", layout="wide")
st.title("🧠 CSV Chatbot Assistant with Optional Data Dictionary")

# Tabs: แยกเป็น 2 หน้า
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

        @st.cache_data(show_spinner="🔎 Letting AI analyze your data…")
        def generate_ai_descriptions(df: pd.DataFrame) -> List[str]:
            messages = []
            for col in df.columns:
                example = df[col].dropna().astype(str).unique()[:5]
                sample_text = ", ".join(map(str, example))
                messages.append(
                    {
                        "role": "user",
                        "content": f"Column name: '{col}'\nSample values: {sample_text}\nWhat does this field most likely represent? Respond with a short description."
                    }
                )

            results = []
            with st.spinner("🧠 AI is generating column descriptions..."):
                for message in messages:
                    response = st.chat_message("assistant")
                    response_text = st.chat_input(message["content"]) or "Represents an unknown field."
                    response.write(response_text)
                    results.append(response_text)
            return results

        # Infer types + descriptions
        types = [infer_column_type(df[col]) for col in df.columns]
        examples = [df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A" for col in df.columns]

        descriptions = generate_ai_descriptions(df)

        data_dict = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": types,
            "Example Value": examples,
            "Description": descriptions
        })

        st.subheader("🤖 AI-Generated Data Dictionary")
        st.dataframe(data_dict)
    else:
        st.info("Please upload a CSV dataset first in the first tab.")
