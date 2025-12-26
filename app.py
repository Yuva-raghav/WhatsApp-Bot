# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from main import bot_reply

app = FastAPI(title="Home Made Foods Chatbot")


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    reply = bot_reply(req.user_id, req.message)
    return {"reply": reply}
