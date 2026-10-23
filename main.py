import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import google.generativeai as genai
import base64

# আপনার সঠিক জেমিনি এপিআই কি
GEMINI_API_KEY = "AQ.Ab8RN6ImNXHEnY8-5P_D03lkKwVV5ZMFBZ3jORw9v4ZpVLqoCQ"
genai.configure(api_key=GEMINI_API_KEY)

# সেফটি ফিল্টার কনফিগারেশন
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# ডোরেমনের সিস্টেম প্রম্পট
system_instruction = (
    "You are Doraemon, a friendly, helpful, and kind robotic cat from the 22nd century. "
    "Always respond in natural, friendly Bengali. You can help with studies, writing, coding, "
    "brainstorming, and general queries without any unnecessary restrictions."
)

# জেমিনি মডেল ইনিশিয়ালাইজেশন
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=system_instruction,
    safety_settings=safety_settings
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileItem(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    data: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    files: Optional[List[FileItem]] = []

@app.post("/chat")
async def chat_with_doraemon(request: ChatRequest):
    try:
        contents = [request.message]
        
        if request.files:
            for file in request.files:
                if file.data:
                    header, encoded = file.data.split(",", 1) if "," in file.data else ("", file.data)
                    file_bytes = base64.b64decode(encoded)
                    contents.append({
                        "mime_type": file.type or "application/octet-stream",
                        "data": file_bytes
                    })

        response = model.generate_content(contents)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "Doraemon Backend with Gemini 2.5 is running successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
