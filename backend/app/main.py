from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load detection model (smaller version for Railway free tier)
MODEL_NAME = "roberta-base-openai-detector"  # ~500MB, but we'll use it for now
tokenizer = None
model = None

class DetectRequest(BaseModel):
    text: str

class DetectResponse(BaseModel):
    ai_score: float
    confidence: str

@app.on_event("startup")
async def load_model():
    global tokenizer, model
    # Load model on startup (Railway will cache it in /app/cache if we set HF_HOME)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()

@app.get("/")
async def root():
    return {"message": "AI Text Detector API"}

@app.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest):
    if not tokenizer or not model:
        raise HTTPException(status_code=503, detail="Model loading")
    
    inputs = tokenizer(request.text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    ai_score = probs[0][1].item() * 100  # Probability of AI-generated
    
    # Determine confidence level (simple heuristic)
    if ai_score > 80 or ai_score < 20:
        confidence = "high"
    elif ai_score > 60 or ai_score < 40:
        confidence = "medium"
    else:
        confidence = "low"
    
    return DetectResponse(ai_score=round(ai_score, 2), confidence=confidence)