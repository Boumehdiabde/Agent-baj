from fastapi import FastAPI
from core.router.router import AgentRouter

app = FastAPI()

router = AgentRouter()

@app.get("/")
async def root():
    return {"message": "Agent OS Running"}

@app.post("/task")
async def run_task(task: str):
    result = router.handle(task)
    return {"result": result}