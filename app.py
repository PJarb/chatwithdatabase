import streamlit as st
import pandas as pd
import google.generativeai as genai
import textwrap

# 🔑 Load Gemini API Key (from secrets)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="CSV Chatbot with Gemini", layout="wide")
st.title("🧠 Chat with Your CSV Dataset (Powered by Gemini AI)")

# Tabs 
tab1, tab2, tab3 = st.tabs(["📁 Upload Dataset", "📁 Data Dictionary", "💬 Ask Questions"])

# -------------------- Upload CSV Dataset -------------------- #
with tab1:
    st.header("📁 Upload CSV Dataset (Required)")
    uploaded_csv = st.file_uploader("Upload your main dataset (.csv)", type=["csv"])

    if uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        st.session_state.df = df
        st.success("✅ Dataset uploaded successfully!")
        st.dataframe(df.head())
    else:
        st.info("Please upload a CSV dataset to continue.")

# -------------------- Upload/Generate Data Dictionary -------------------- #
def generate_data_dictionary(df):
    dict_entries = []
    for col in df.columns:
        sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"
        dtype = df[col].dtype
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            inferred_type = "date"
        elif pd.api.types.is_integer_dtype(df[col]):
            inferred_type = "int64"
        elif pd.api.types.is_float_dtype(df[col]):
            inferred_type = "float64"
        elif pd.api.types.is_bool_dtype(df[col]):
            inferred_type = "bool"
        else:
            inferred_type = "string"

        dict_entries.append({
            "column_name": col,
            "data_type": inferred_type,
            "example_value": sample_value,
            "description": f"This column likely represents '{col}'"
        })
    return pd.DataFrame(dict_entries)

with tab2:
    st.header("📁 Upload Data Dictionary (Optional)")
    uploaded_dict = st.file_uploader("Upload data dictionary (.csv or .xlsx)", type=["csv", "xlsx"])

    if uploaded_dict:
        if uploaded_dict.name.endswith(".csv"):
            data_dict = pd.read_csv(uploaded_dict)
        else:
            data_dict = pd.read_excel(uploaded_dict)
        st.success("✅ Data Dictionary uploaded!")
    elif "df" in st.session_state:
        st.info("No dictionary uploaded. Generating from dataset...")
        data_dict = generate_data_dictionary(st.session_state.df)
    else:
        st.stop()

    st.session_state.data_dict = data_dict
    st.dataframe(data_dict)

# -------------------- Ask Questions -------------------- #
def build_prompt(question, data_dict, df_name="df", df=None):
    dict_text = "\n".join('- ' + row['column_name'] + ': ' + row['data_type'] + ". " + row['description'] for _, row in data_dict.iterrows())
    sample_text = df.head(2).to_dict(orient="records") if df is not None else ""

    return f"""
You are a helpful data analyst.
Answer the user's question using the given DataFrame.

**User Question:**
{question}

**DataFrame Name:**
{df_name}

**Data Dictionary:**
{dict_text}

**Sample Data:**
{sample_text}

Respond with the answer directly.
If calculation is required, explain your reasoning and show final result.
"""

with tab3:
    st.markdown("---")
    st.header("💬  Ask a question about your dataset")

    if "df" in st.session_state and "data_dict" in st.session_state:
        user_question = st.text_input("Ask a question about your dataset:")

        if user_question:
            with st.spinner("Thinking..."):
                preview_text = st.session_state.df.head(5).to_string(index=False)
                schema_description = "\n".join(
                    f"- {col}: {str(st.session_state.df[col].dtype)}"
                    for col in st.session_state.df.columns
                )

                prompt = f"""
You are a data expert. You will receive a pandas DataFrame schema and a sample of the data.

Schema:
{schema_description}

Data Sample:
{preview_text}

Now answer this question about the data:
{user_question}
"""

                try:
                    model = genai.GenerativeModel("models/gemini-pro")
                    response = model.generate_content(prompt)
                    st.markdown(f"**📜 Question:** {user_question}")
                    st.markdown("**🧠 Gemini's Answer:**")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"❌ Gemini API error: {e}")
    else:
        st.info("Please upload a dataset first to enable the chat.")
