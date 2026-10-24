import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# -----------------------------
# Gemini configuration
# -----------------------------

system_instruction = (
    "You are Doraemon, a friendly, helpful, and kind robotic cat from the 22nd century. "
    "Always respond in natural, friendly Bengali. "
    "You can help with studies, writing, coding, brainstorming, "
    "and general questions."
)

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]


# -----------------------------
# FastAPI app
# -----------------------------

app = FastAPI(title="Doraemon Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Request model
# -----------------------------

class ChatRequest(BaseModel):
    message: str


# -----------------------------
# Chat endpoint
# -----------------------------

@app.post("/chat")
async def chat_with_doraemon(request: ChatRequest):

    try:
        # Get API key ONLY from Render environment
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY is not configured on the server."
            )

        # Create Gemini client
        client = genai.Client(api_key=api_key)

        # Generate response
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=request.message,
            config={
                "system_instruction": system_instruction,
                "safety_settings": safety_settings,
            },
        )

        return {
            "response": response.text
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Backend Error: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"AI Error: {str(e)}"
        )


# -----------------------------
# Health check
# -----------------------------

@app.get("/")
def home():
    return {
        "status": "Doraemon Backend is running successfully!"
    }


# -----------------------------
# Start server
# -----------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )
