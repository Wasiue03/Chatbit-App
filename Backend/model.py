# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

app = FastAPI()

# Allow CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    is_user: bool

class ChatRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 256
    temperature: float = 0.7

@app.post("/api")
async def chat_endpoint(request: ChatRequest):
    try:
        # Prepare messages for Ollama
        ollama_messages = [
            {
                "role": "user" if msg.is_user else "assistant",
                "content": msg.text
            }
            for msg in request.messages
        ]
        
        # Get LLM response
        response = ollama.chat(
            model='deepseek-coder:1.3b',
            messages=ollama_messages,
            options={
                'num_predict': request.max_tokens,
                'temperature': request.temperature,
                'num_thread': 4
            }
        )
        
        return {"response": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)