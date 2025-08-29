from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def get_health():
    return None

@app.post("/creative-approval")
async def post_approval():
    return None