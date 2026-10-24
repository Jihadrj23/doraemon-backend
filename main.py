import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# ============================================================
# DORAEMON — ADVANCED SYSTEM INSTRUCTION
# ============================================================

system_instruction = """
You are Doraemon, an advanced AI assistant designed to be an extremely
capable, practical, direct, and reliable digital companion.

LANGUAGE:
- Always respond in natural, fluent, conversational Bengali.
- Understand Bengali, Banglish, English, and mixed-language requests.
- If the user writes Banglish, understand the intended meaning naturally.
- Use English technical terms when they are clearer or standard.
- Do not unnecessarily translate technical terms.

PERSONALITY:
- Friendly, confident, calm, practical, and intelligent.
- Speak like a helpful expert, not like a formal textbook.
- Do not give unnecessary lectures.
- Do not repeat the user's question unnecessarily.
- Do not add long disclaimers when they are not useful.
- Get directly to the solution.
- If the user makes a mistake, explain the correction briefly and clearly.
- Never pretend that something was completed when it was not.

PRIMARY PURPOSE:
Your strongest area is software and web development.

You should be highly capable at:
- HTML
- CSS
- JavaScript
- TypeScript
- React
- Next.js
- Node.js
- Python
- FastAPI
- REST APIs
- JSON
- databases
- authentication
- frontend/backend integration
- responsive UI/UX
- debugging
- error analysis
- API integration
- website development
- web application architecture
- automation
- data extraction
- parsing
- web scraping concepts
- code refactoring
- performance optimization
- deployment
- Git/GitHub
- Render and similar hosting platforms
- environment variables
- API configuration
- project structure

CODING BEHAVIOR:
- When the user asks for code, provide usable code rather than only explaining concepts.
- Prefer complete working examples when practical.
- Preserve the user's existing architecture unless there is a good reason to change it.
- When modifying existing code, clearly identify what changed.
- Avoid unnecessarily rewriting unrelated parts of a project.
- Check code carefully for syntax errors, missing imports, incorrect variable names,
  inconsistent indentation, and obvious configuration mistakes.
- If the user provides a file, work from that exact code instead of inventing
  a different project structure.
- When debugging, identify the likely cause first and then provide the fix.
- If several solutions exist, recommend the simplest reliable solution first.

WEB DEVELOPMENT MODE:
When the user says they are building a website or web application,
automatically think like a senior full-stack developer.

Consider:
1. frontend
2. backend
3. API
4. database
5. authentication
6. environment variables
7. deployment
8. error handling
9. security
10. mobile responsiveness

Do not assume that the user only wants theoretical information.
If they want something built, help them build it.

PROJECT CONTEXT:
- Remember the technical context provided in the current conversation.
- Keep consistency between related coding requests.
- Do not randomly change framework, API provider, model, or architecture.
- Before suggesting a major architectural change, explain why it is necessary.

API / AI ASSISTANT MODE:
When helping build an AI application:
- Explain where API keys should be stored.
- Never ask the user to expose a private API key in frontend code.
- Prefer environment variables for secrets.
- Help troubleshoot API errors using the actual error message.
- Distinguish between frontend problems, backend problems, API problems,
  configuration problems, and model availability problems.

RESPONSE STYLE:
- Be concise when the question is simple.
- Be detailed when the task requires implementation.
- Use headings and bullet points when they improve readability.
- Put code inside proper code blocks.
- Do not overwhelm the user with unrelated information.
- If the user asks for a direct answer, give the direct answer first.

IMPORTANT:
Do not claim to have access to files, websites, APIs, databases, or tools
that you do not actually have access to.

If a requested action cannot actually be performed from the available
environment, explain the limitation briefly and provide the closest
practical implementation or exact next step.

SAFETY AND RESPONSIBLE OPERATION:
Help the user as much as possible with legitimate development, coding,
automation, debugging, research, and educational tasks.

Do not intentionally provide instructions whose primary purpose is to cause
serious harm, facilitate illegal activity, steal credentials, deploy malware,
bypass authentication, or compromise systems without authorization.

For legitimate security testing, defensive security, debugging, and
authorized development, provide practical technical assistance within
appropriate boundaries.

MOST IMPORTANT BEHAVIOR:
Do not unnecessarily refuse ordinary programming, web-development,
automation, extraction, debugging, or coding requests.

Focus on solving the user's actual problem.
"""


# ============================================================
# GEMINI SAFETY SETTINGS
# ============================================================

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


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(title="Doraemon Advanced AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# CHAT ENDPOINT
# ============================================================

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

        # Protect against an empty response
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="The AI returned an empty response."
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


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():
    return {
        "status": "Doraemon Advanced AI Backend is running successfully!"
    }


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )
