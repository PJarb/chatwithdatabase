import streamlit as st
import pandas as pd
import google.generativeai as genai
import textwrap

# 🔑 Load Gemini API Key (จาก secrets)
try:
    key = st.secrets["gemini_api_key"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
except Exception as e:
    st.error(f"❌ Failed to load Gemini API: {e}")
    st.stop()

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
def build_code_prompt(question, data_dict, df_name="df", df=None):
    dict_text = "\n".join('- ' + row['column_name'] + ': ' + row['data_type'] + ". " + row['description'] for _, row in data_dict.iterrows())
    sample_text = df.head(2).to_dict(orient="records") if df is not None else ""
    return f"""
You are a helpful Python code generator.
Your goal is to write Python code snippets based on the user's question and the provided DataFrame information.

Here's the context:
**User Question:**
{question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{dict_text}

**Sample Data (Top 2 Rows):**
{sample_text}

**Instructions:**
1. Write Python code that addresses the user's question by querying or manipulating the DataFrame.
2. Use the `exec()` function to execute the generated code.
3. Do not import pandas.
4. Change date column type to datetime if needed.
5. Store the result of the executed code in a variable named `ANSWER`.
6. Assume the DataFrame is already loaded into a pandas DataFrame object named `{df_name}`.
7. Keep the code concise and focused on answering the question.
"""

def clean_code_block(text):
    return text.replace("```python", "").replace("```", "").strip()

with tab3:
    st.markdown("---")
    st.header("💬 Ask a question about your dataset")

    if "df" in st.session_state and "data_dict" in st.session_state:
        user_question = st.text_input("Ask a question about your dataset:")
        if user_question:
            with st.spinner("Thinking..."):
                try:
                    prompt = build_code_prompt(
                        question=user_question,
                        data_dict=st.session_state.data_dict,
                        df_name="df",
                        df=st.session_state.df
                    )
                    response = model.generate_content(prompt)
                    code = clean_code_block(response.text)

                    # Execute the generated code and retrieve ANSWER
                    try:
                        exec_locals = {"df": st.session_state.df.copy()}
                        exec(code, {}, exec_locals)
                        answer = exec_locals.get("ANSWER", "No variable named 'ANSWER' found.")
                    except Exception as e:
                        answer = f"❌ Error while executing generated code: {e}"

                    # Summarize result
                    explanation_prompt = f"""
the user asked: {user_question},
here is the results: {answer}
answer the question and summarize the answer,
include your opinions of the persona of this customer
"""
                    summary = model.generate_content(explanation_prompt)

                    # Display
                    st.markdown(f"**📜 Question:** {user_question}")
                    st.markdown("**🧠 Gemini's Summary:**")
                    st.write(summary.text)
                except Exception as e:
                    st.error(f"❌ Gemini API error: {e}")
    else:
        st.info("Please upload a dataset first to enable the chat.")

st.caption(f"Gemini SDK version: {genai.__version__}")
