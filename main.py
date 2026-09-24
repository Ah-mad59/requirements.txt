from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI(title="AI Text Processor Micro-SaaS")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class TextRequest(BaseModel):
    text: str
    action: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منسق ومحلل النصوص الذكي</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="bg-gray-950 text-white font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-4xl mx-auto bg-gray-900 border border-gray-800 rounded-2xl shadow-2xl p-6 md:p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl font-black text-amber-500 mb-2">منسق ومحلل النصوص الذكي ⚡</h1>
            <p class="text-gray-400 text-sm">أداتك السريعة لتنظيف، تلخيص، وإعادة صياغة النصوص بالذكاء الاصطناعي</p>
        </div>

        <div class="space-y-6">
            <div>
                <label class="block text-sm font-bold text-gray-300 mb-2">النص المراد معالجته:</label>
                <textarea id="inputText" rows="6" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-4 text-white focus:outline-none focus:border-amber-500 transition" placeholder="ألصق المقال أو النص هنا..."></textarea>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <button onclick="processText('summarize')" class="bg-amber-500 hover:bg-amber-600 text-gray-950 font-bold py-3 rounded-xl transition shadow-lg">تلخيص النص 📝</button>
                <button onclick="processText('format')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition shadow-lg">إصلاح وتنسيق الأخطاء 🧹</button>
                <button onclick="processText('paraphrase')" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-xl transition shadow-lg">إعادة صياغة احترافية ✍️</button>
            </div>

            <div id="loading" class="hidden text-center text-amber-400 font-bold animate-pulse">جاري معالجة النص بواسطة الذكاء الاصطناعي... ⏳</div>

            <div>
                <label class="block text-sm font-bold text-gray-300 mb-2">النتيجة:</label>
                <div id="outputText" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-4 min-h-[150px] text-gray-200 whitespace-pre-wrap">النتيجة ستظهر هنا...</div>
            </div>
        </div>
    </div>

    <script>
        async function processText(action) {
            const text = document.getElementById('inputText').value;
            const outputDiv = document.getElementById('outputText');
            const loadingDiv = document.getElementById('loading');

            if (!text.trim()) {
                alert('الرجاء إدخال نص أولاً!');
                return;
            }

            loadingDiv.classList.remove('hidden');
            outputDiv.innerText = '';

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, action: action })
                });

                const data = await response.json();
                if (response.ok) {
                    outputDiv.innerText = data.result;
                } else {
                    outputDiv.innerText = 'خطأ: ' + (data.detail || 'حدث خطأ ما');
                }
            } catch (error) {
                outputDiv.innerText = 'حدث خطأ في الاتصال بالخادم.';
            } finally {
                loadingDiv.classList.add('hidden');
            }
        }
    </script>
</body>
</html>
"""

@app.post("/process")
def process_text(req: TextRequest):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="مفتاح OpenAI API غير محدد في خادم الاستضافة.")
    
    prompts = {
        "summarize": "قم بتلخيص النص التالي باختصار واحترافية باللغة العربية:",
        "format": "قم بتصحيح الأخطاء الإملائية والنحوية وتنسيق النص التالي بشكل احترافي:",
        "paraphrase": "قم بإعادة صياغة النص التالي بأسلوب إبداعي واحترافي باللغة العربية:"
    }

    system_prompt = prompts.get(req.action, "قم بتحسين النص التالي:")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.text}
            ],
            temperature=0.7
        )
        result = response.choices[0].message.content
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
