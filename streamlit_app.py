import streamlit as st
import requests
import json

st.set_page_config(page_title="SEO Content Generator", layout="wide")
st.title("SEO Content Generator")


# Input fields
uploaded_data = ""
file = st.file_uploader("Upload BDC JSON file", type=["json", "txt"])
if file:
    uploaded_data = file.read().decode("utf-8")

pasted_data = st.text_area("Or paste BDC data (JSON or text)", value="", height=200)
city = st.text_input("City")
country = st.text_input("Country")
currency = st.text_input("Currency")
content_type = st.selectbox(
    "Content Type",
    ["hotels-in-city", "HDP", "OYO-travelblog"],
    index=0
)

if st.button("Generate SEO Content"):
    # Prefer uploaded file, else use pasted data
    bdc_data = uploaded_data if uploaded_data.strip() else pasted_data.strip()
    if not city.strip() or not country.strip() or not currency.strip() or not bdc_data:
        st.error("Please fill all fields and provide BDC data (upload or paste).")
    else:
        # Try to parse as JSON, else send as raw
        try:
            bdc_json = json.loads(bdc_data)
        except Exception:
            bdc_json = {"raw": bdc_data}
        payload = {
            "bdc_data": bdc_json,
            "city": city,
            "country": country,
            "currency": currency,
            "content_type": content_type
        }
        with st.spinner("Generating content..."):
            try:
                resp = requests.post("http://127.0.0.1:8000/generate-content", json=payload)
                if resp.ok:
                    data = resp.json()
                    st.success("Content generated!")
                    st.text_area("Generated Content", value=data.get("content", str(data)), height=400)
                else:
                    st.error(f"Error: {resp.status_code}\n{resp.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
