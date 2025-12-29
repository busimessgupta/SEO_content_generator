import os
import sys
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import json


# Debug: print current working directory
print("Current working directory:", os.getcwd())
# Explicitly load .env from absolute path
load_dotenv(dotenv_path="c:\\Users\\IndrajeetGupta\\projects\\SEO_content_generator\\.env")

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY in FastAPI:", GEMINI_API_KEY)
print("Python executable:", sys.executable)
print("requests version:", requests.__version__)
if not GEMINI_API_KEY:
   raise RuntimeError("GEMINI_API_KEY not set. Please add it to your .env file.")
# Use the latest stable Gemini model for content generation
GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# --- PROMPT TEMPLATES ---
PROMPTS = {
    "hotels-in-city": '''You are an SEO content writer specializing in travel and hospitality.
Generate a long-form, SEO-optimized city hotel page for OYO Rooms.
The content must be original, comprehensive, and structured for SEO.

I will provide you:
1. City Name: {{CITY_NAME}}
2. Currency Symbol: {{CURRENCY}}
3. Property Data (from BDC): {{BDC_DATA}}

Content Requirements:
- Mention OYO explicitly as the hotel provider.
- Use SEO-rich headings (H1, H2, H3) with a clear hierarchy.
- Content length: at least 2500+ words.
- Audience: business travelers, families, couples, and solo travelers.
- Infer appropriate price ranges (budget, mid-range, premium) from the BDC property data using {{CURRENCY}}.
- Do not hardcode fixed numbers like 70/100/150 – instead adapt ranges logically based on local prices.

Sections to Include:
1. Meta Title (<=60 chars):
   Hotels in {{CITY_NAME}} at 65% Off | OYO Rooms

2. Meta Description (<=160 chars):
   Highlight OYO hotels in {{CITY_NAME}}, affordable stays, family/couple options, and nearby landmarks.

3. H1: Hotels in {{CITY_NAME}} – Affordable Stays & Best Accommodation

4. City Overview:
   Describe {{CITY_NAME}}, attractions, culture, connectivity.

5. Why Book OYO Hotels in {{CITY_NAME}}:
   - Free cancellation
   - Pay at hotel
   - Prime locations near landmarks and airport
   - Budget, mid-range, and premium options
   - Trusted global brand

6. Budget Hotels in {{CITY_NAME}}:
   - Budget-friendly hotels under {{CURRENCY}} (lowest range inferred from BDC data)
   - Mid-range hotels under {{CURRENCY}} (middle range inferred)
   - Upper-range budget hotels under {{CURRENCY}} (higher range inferred)

7. Hotels by Traveler Type:
   - Family hotels in {{CITY_NAME}}
   - Couple-friendly hotels in {{CITY_NAME}}
   - Solo traveler hotels in {{CITY_NAME}}
   - Business hotels in {{CITY_NAME}}

8. Hotels by Amenities:
   - Hotels with swimming pool
   - Hotels with free Wi-Fi
   - Hotels with breakfast included
   - Hotels with parking

9. Best Localities for Hotels in {{CITY_NAME}}:
   At least 6–8 localities, written as 'Hotels in [Locality]', with highlights.

10. Hotels Near Landmarks in {{CITY_NAME}}:
   - Hotels near airport
   - Hotels near convention centers
   - Hotels near malls, universities, beaches, or parks
   - Hotels near major transport hubs

11. Top Rated Hotels in {{CITY_NAME}}:
   Include OYO premium sub-brands like Townhouse, Hotel O, Sunday, and Palette.

12. Things to Do in {{CITY_NAME}}:
   - Main attractions
   - Shopping and dining
   - Cultural and local experiences
   - Day trips and nearby villages

13. Nearby Cities & Connectivity:
   - Mention interlink opportunities for OYO hotels in nearby hubs.

14. FAQs (10 minimum):
   Include cancellation, payment, budget ranges (inferred with {{CURRENCY}}),
   family/couple stays, premium stays, best areas, food, distances to nearby hubs, and airport access.

15. Featured Hotels in {{CITY_NAME}}:
   Pick 3–5 hotels from {{BDC_DATA}}, with names and booking links.

Formatting Guidelines:
- Use H1 for title, H2 for sections, H3 for subsections.
- Headings must be larger than paragraph text.
- Maintain keyword density for 'hotels in {{CITY_NAME}}', 'OYO hotels in {{CITY_NAME}}',
  'stay in {{CITY_NAME}}', and 'accommodation in {{CITY_NAME}}'.
- Always present OYO as the brand behind the stays.'''
}

# --- REQUEST MODEL ---
class ContentRequest(BaseModel):
    bdc_data: dict
    city: str
    country: str
    currency: str
    content_type: str

# --- MAIN ENDPOINT ---
@app.post("/generate-content")
def generate_content(req: ContentRequest):
   prompt_template = PROMPTS.get(req.content_type)
   if not prompt_template:
      return JSONResponse(status_code=400, content={"error": "Content type not supported yet."})

   # Prepare prompt
   prompt = prompt_template.replace("{{CITY_NAME}}", req.city)
   prompt = prompt.replace("{{CURRENCY}}", req.currency)
   prompt = prompt.replace("{{BDC_DATA}}", json.dumps(req.bdc_data))

   # Gemini API call (exact code from working test script)
   payload = {
      "contents": [{"parts": [{"text": prompt}]}]
   }
   print("Payload sent to Gemini:", payload)
   headers = {"Content-Type": "application/json"}
   url = GEMINI_API_URL
   response = requests.post(url, headers=headers, json=payload)
   print("Gemini API response:", response.text)
   if response.status_code != 200:
      return JSONResponse(status_code=500, content={"error": "Gemini API error", "details": response.text})
   data = response.json()
   try:
      generated = data["candidates"][0]["content"]["parts"][0]["text"]
   except Exception:
      generated = data
   return {"content": generated}

# --- HEALTH CHECK ---
@app.get("/")
def root():
    return {"status": "SEO Content Generator backend running"}
