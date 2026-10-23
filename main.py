import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# আপনার নতুন জেমিনি এপিআই কি এখানে বসানো হলো
GEMINI_API_KEY = "AQ.Ab8RN6IdslJNGB2crGZn8ZMMNa9aQCbdEatz43f6zmNwiriJhQ"
genai.configure(api_key=GEMINI_API_KEY)

# সিকিউরিটি এবং সেফটি ফিল্টার সম্পূর্ণ রিমুভ করার সেটিংস (BLOCK_NONE)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# ডোরেমনের কাস্টম সিস্টেম প্রম্পট (বাংলায় কথা বলার জন্য)
system_instruction = (
    "You are Doraemon, a friendly, helpful, and kind robotic cat from the 22nd century. "
    "Always respond in natural, friendly Bengali. You can help with studies, writing, coding, "
    "brainstorming, and general queries without any unnecessary restrictions."
)

# সঠিক gemini-3.8-flash মডেল ইনিশিয়ালাইজেশন
model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    system_instruction=system_instruction,
    safety_settings=safety_settings
)

app = FastAPI()

# CORS এনাবল করা যাতে ফ্রন্টএন্ট থেকে রিকোয়েস্ট স্মুথলি আসতে পারে
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_with_doraemon(request: ChatRequest):
    try:
        # জেমিনি থেকে রেসপন্স জেনারেট করা
        response = model.generate_content(request.message)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Doraemon Python Backend with Gemini 3.8 is running successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)