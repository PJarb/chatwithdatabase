import numpy as np
import pandas as pd

def generate_data_dictionary(df):
    dict_entries = []

    for col in df.columns:
        sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "N/A"

        # ตรวจสอบชนิดข้อมูล
        dtype = df[col].dtype

        # ตรวจจับ datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            inferred_type = "date"
        elif pd.api.types.is_integer_dtype(df[col]):
            inferred_type = "int64"
        elif pd.api.types.is_float_dtype(df[col]):
            inferred_type = "float64"
        elif pd.api.types.is_bool_dtype(df[col]):
            inferred_type = "bool"
        elif pd.api.types.is_string_dtype(df[col]) or dtype == "object":
            # ลองแปลงเป็น datetime ดูเพื่อเช็คว่ามีโอกาสเป็น date หรือไม่
            try:
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
            "Example Value": sample_value,
            "Description": "Auto-generated description (can be edited)"
        })

    return pd.DataFrame(dict_entries)
