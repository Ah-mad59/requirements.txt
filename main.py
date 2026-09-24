import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai

app = FastAPI()
templates = Jinja2Templates(directory="templates")

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
  return templates.TemplateResponse(
      "index.html", {"request": request, "result": ""}
  )


@app.post("/process", response_class=HTMLResponse)
async def process_text(
    request: Request, text: str = Form(...), action: str = Form(...)
):
  prompts = {
      "fix": (
          "قم بتصحيح الأخطاء الإملائية والنحوية وتنسيق النص التالي بدقة:"
      ),
      "summarize": "قم بتلخيص النص التالي بوضوح واختصار:",
      "rewrite": "قم بإعادة صياغة النص التالي بأسلوب احترافي وبليغ:",
  }

  selected_prompt = prompts.get(
      action, "قم بتحسين النص وإعادة صياغته:"
  ) + f"\n\n{text}"

  try:
    response = model.generate_content(selected_prompt)
    result = response.text
  except Exception as e:
    result = f"حدث خطأ أثناء المعالجة: {str(e)}"

  return templates.TemplateResponse(
      "index.html",
      {"request": request, "result": result, "original_text": text},
  )
