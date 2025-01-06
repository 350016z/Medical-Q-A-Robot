from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from transformers import pipeline
import torch
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import markdown2

app = FastAPI()

model_id = "Johhny1201/llama3.2_1b_med_QA_3"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.float32,  # 適合cpu環境
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
def predict(request: Request, question: str = Form(...)):

    messages = [
        {"role": "system", "content": "You are a helpful medical diagnostic assistant, you will help the user to do the best of your ability"},
        {"role": "user", "content": question},
    ]

    outputs = pipe(
        messages,
        max_new_tokens=256,
        temperature=0.4,
    )

    generated_texts = outputs[0]["generated_text"]
    raw_answer = generated_texts[-1]["content"] if generated_texts else "Unable to respond！ Try again！"

    rendered_answer = markdown2.markdown(raw_answer)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "question": question,
        "analysis": rendered_answer,
    })
