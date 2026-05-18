from fastapi import FastAPI

app=FastAPI()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/generate")
def generate():
    return{"response":"placeholder response"}
