!pip install -q -U google-generativeai
import google.generativeai as genai
genai.configure(api_key='AIzaSyBdf4nh_jx7Jq3M8lZ4Zbfim6GULaNr9iI')
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
