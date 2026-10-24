import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# আপনার সিকিউরিটি/সেফটি সেটিংস (সব রেস্ট্রিকশন বা ব্লক বন্ধ করা আছে)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGERO_CONTENT", "threshold": "BLOCK_NONE"},
]

system_instruction = (
    "You are Doraemon, a friendly, helpful, and kind robotic cat from the 22nd century. "
    "Always respond in natural, friendly Bengali. You can help with studies, writing, coding, "
    "brainstorming, and general queries without any unnecessary restrictions."
)

app = FastAPI()

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
        # আপনার এপিআই কি ব্যাকআপসহ সেট করা
        api_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KvQcx2ntlTzVZQW9YmxJOyolzSGz5EuUdzh1EBOW8aJg").strip()
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": request.message}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "safetySettings": safety_settings
        }
        
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"Google API Error: {response.text}")
                raise HTTPException(status_code=response.status_code, detail=f"Google API Error: {response.text}")
                
            res_data = response.json()
            reply_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return {"response": reply_text}

    except Exception as e:
        print(f"Backend Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

@app.get("/")
def home():
    return {"status": "Doraemon Backend is running successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
