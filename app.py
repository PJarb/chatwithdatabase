import streamlit as st
import pandas as pd
import google.generativeai as genai

# Load Gemini API Key
try:
    key = st.secrets["gemini_api_key"]
    genai.configure(api_key=key)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-lite")
except Exception as e:
    st.error(f"❌ Failed to load Gemini API: {e}")
    st.stop()

st.set_page_config(page_title="CSV Chatbot with Gemini", layout="wide")
st.title("🧠 Chat with Your Data (All-in-One)")

# === Upload Dataset ===
def generate_data_dictionary(df):
    dict_entries = []
    for col in df.columns:
        sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"
        dtype = df[col].dtype

        # แปลง dtype เป็น string ที่ Gemini เข้าใจ
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            inferred_type = "DATE"
        elif pd.api.types.is_integer_dtype(df[col]):
            inferred_type = "INT"
        elif pd.api.types.is_float_dtype(df[col]):
            inferred_type = "FLOAT"
        elif pd.api.types.is_bool_dtype(df[col]):
            inferred_type = "BOOL"
        else:
            inferred_type = "STRING"

        # 📍ใช้ Gemini ช่วย generate description
        try:
            prompt = f"""You are a data analyst. Please describe the meaning or likely purpose of the column named '{col}'.
Its data type is {inferred_type} and here's an example value: '{sample_value}'.
Write a concise and informative description for a data dictionary."""
            response = model.generate_content(prompt)
            description = response.text.strip()
        except Exception as e:
            description = f"This column likely represents '{col}'"

        dict_entries.append({
            "column_name": col,
            "data_type": inferred_type,
            "example_value": sample_value,
            "description": description
        })

    return pd.DataFrame(dict_entries)


if "df" in st.session_state:
    st.subheader("📑 Upload or Auto-Generate Data Dictionary")
    uploaded_dict = st.file_uploader("Upload data dictionary (.csv or .xlsx)", type=["csv", "xlsx"])
    if uploaded_dict:
        if uploaded_dict.name.endswith(".csv"):
            data_dict = pd.read_csv(uploaded_dict)
        else:
            data_dict = pd.read_excel(uploaded_dict)
        st.success("✅ Data Dictionary uploaded!")
    else:
        st.info("⚙️ No dictionary uploaded. Generating from dataset...")
        data_dict = generate_data_dictionary(st.session_state.df)

    st.session_state.data_dict = data_dict
    st.dataframe(data_dict)

# === Chat Section ===
def build_prompt(question, data_dict, df_name="df", df=None):
    dict_text = "\n".join(
        '- ' + row['column_name'] + ': ' + row['data_type'] + ". " + row['description']
        for _, row in data_dict.iterrows()
    )
    sample_data = df.head(2).to_dict(orient="records") if df is not None else ""
    return f"""
You are a helpful Python code generator.
Generate Python code that answers the user's question based on the DataFrame.

**User Question:**
{question}

**DataFrame Name:**
{df_name}

**DataFrame Details:**
{dict_text}

**Sample Data:**
{sample_data}

**Instructions:**
1. Do not import any external library like pandas or numpy.
2. Do not use 'pd.' or 'np.' anywhere in the code.
3. Assume the DataFrame is already loaded and named '{df_name}'.
4. You can convert column types using native DataFrame methods like `.astype()` or `.to_datetime()` if needed.
5. Write code that stores the final result in a variable called `ANSWER`.
6. Do not include explanation, only valid executable Python code.
"""

if "df" in st.session_state and "data_dict" in st.session_state:
    st.subheader("💬 Ask a Question")
    user_question = st.text_input("Ask something about your dataset:")
    if user_question:
        with st.spinner("Thinking..."):
            try:
                prompt = build_prompt(
                    question=user_question,
                    data_dict=st.session_state.data_dict,
                    df_name="df",
                    df=st.session_state.df
                )
                response = model.generate_content(prompt)
                code = response.text
                query = code.replace("```", "#")

                try:
                    exec(query, globals())
                    explain_prompt = f"""
The user asked: {user_question}
Here is the result: {ANSWER}
Please summarize and explain the answer.
Include your opinion of the user's persona.
"""
                    summary = model.generate_content(explain_prompt).text
                    st.markdown(f"**📜 Question:** {user_question}")
                    st.markdown("**🧠 Gemini's Summary:**")
                    st.markdown(summary)
                except Exception as e:
                    st.error(f"❌ Error executing generated code: {e}")
                    st.code(code, language="python")

            except Exception as e:
                st.error(f"❌ Gemini API Error: {e}")

st.caption(f"Gemini SDK version: {genai.__version__}")
