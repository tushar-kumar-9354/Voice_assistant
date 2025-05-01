import google.generativeai as genai

genai.configure(api_key="AIzaSyDzd5LmtCReZCVKSTOQkOnQ7vmcDC0_p30")
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello, world!")
print(response.text)
