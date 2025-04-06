import streamlit as st
import pandas as pd

st.set_page_config(page_title="CSV Upload", layout="centered")

st.title("📂 Upload CSV for Chat with Data")

# ปุ่มให้อัปโหลดไฟล์ CSV
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# เช็คว่ามีไฟล์อัปโหลดหรือยัง
if uploaded_file is not None:
    # อ่านข้อมูล CSV ด้วย Pandas
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Uploaded Data Preview")
    st.dataframe(df.head())  # แสดง 5 แถวแรก

    # ตัวเลือก checkbox เพื่อควบคุมการวิเคราะห์ข้อมูล
    if st.checkbox("Analyze CSV Data with AI"):
        st.success("✅ CSV Analysis activated!")

        # 🔍 ตัวอย่างการวิเคราะห์เบื้องต้น
        st.subheader("🔎 Basic Data Insights")
        st.write("Number of Rows:", df.shape[0])
        st.write("Number of Columns:", df.shape[1])
        st.write("Column Names:", list(df.columns))

        # ใส่การวิเคราะห์อื่น ๆ ได้ เช่น การหาค่าที่ซ้ำหรือข้อมูลที่ขาดหาย
        st.write("Missing Values:")
        st.write(df.isnull().sum())

else:
    st.info("Please upload a CSV file to get started.")
