"""Main FastAPI application."""
import hmac
import logging
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents import AutomationAgent, CodingAgent, MarketingAgent, ResearchAgent
from config import settings
from core.llm import get_llm_provider
from core.router import AgentRouter
from core.security import security_manager

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent OS",
    description="Multi-agent system for specialized task execution",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

router: Optional[AgentRouter] = None
agents = {}
llm_provider = None


@app.on_event("startup")
async def startup_event():
    """Initialize configured services; keep health/docs available without an LLM key."""
    global router, agents, llm_provider
    logger.info("Starting Agent OS in %s mode", settings.FASTAPI_ENV)
    router = AgentRouter()
    agents = {}
    llm_provider = None

    provider_config = next(
        ((name, key) for name, key in (
            ("openai", settings.OPENAI_API_KEY),
            ("anthropic", settings.ANTHROPIC_API_KEY),
            ("google", settings.GOOGLE_API_KEY),
        ) if key),
        None,
    )
    if provider_config is None:
        logger.warning("No LLM API key configured; task execution is unavailable")
        return

    provider_name, api_key = provider_config
    try:
        llm_provider = get_llm_provider(provider_name, api_key)
        agents.update({
            "research": ResearchAgent(llm_provider),
            "coding": CodingAgent(llm_provider),
            "automation": AutomationAgent(llm_provider),
            "marketing": MarketingAgent(llm_provider),
        })
        logger.info("Initialized %d agents using %s", len(agents), provider_name)
    except Exception:
        logger.exception("Could not initialize LLM provider %s", provider_name)
        # Do not expose provider details or prevent health/docs from starting.
        agents = {}
        llm_provider = None


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Agent OS")


class TaskRequest(BaseModel):
    """Task execution request."""
    task: str = Field(min_length=1, max_length=20_000)
    agent_type: Optional[str] = None


class TaskResponse(BaseModel):
    task: str
    agent_type: str
    result: str
    status: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    agents_available: int


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> str:
    """Verify an API key using constant-time comparison."""
    configured_key = settings.API_KEY
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    configured_match = bool(configured_key) and hmac.compare_digest(x_api_key, configured_key)
    if not configured_match and not security_manager.verify_api_key(x_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return x_api_key


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy" if agents else "degraded",
        environment=settings.FASTAPI_ENV,
        agents_available=len(agents),
    )


@app.get("/agents")
async def list_agents(api_key: str = Depends(verify_api_key)):
    if router is None:
        raise HTTPException(status_code=503, detail="Application is not initialized")
    return [
        {"name": agent.name, "description": router.get_agent_description(name), "status": "active"}
        for name, agent in agents.items()
    ]


@app.post("/execute", response_model=TaskResponse)
@app.post("/task", response_model=TaskResponse, include_in_schema=False)
async def execute_task(request: TaskRequest, api_key: str = Depends(verify_api_key)):
    if not request.task.strip():
        raise HTTPException(status_code=422, detail="Task must not be blank")
    if router is None:
        raise HTTPException(status_code=503, detail="Application is not initialized")
    if not agents:
        raise HTTPException(status_code=503, detail="No LLM provider is configured")

    agent_type = request.agent_type or router.route_task(request.task)["agent_type"]
    if agent_type not in agents:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
    try:
        logger.info("Executing task with %s agent", agent_type)
        result = await agents[agent_type].execute(request.task)
        return TaskResponse(task=request.task, agent_type=agent_type, result=result, status="completed")
    except Exception as exc:
        logger.exception("Task execution failed")
        raise HTTPException(status_code=502, detail="Task execution failed; check server logs") from exc


@app.get("/agent/{agent_type}/info")
async def get_agent_info(agent_type: str, api_key: str = Depends(verify_api_key)):
    if agent_type not in agents:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_type}")
    return agents[agent_type].get_agent_info()


@app.post("/token")
async def generate_token(user_id: str, api_key: str = Depends(verify_api_key)):
    if not user_id.strip():
        raise HTTPException(status_code=422, detail="user_id must not be blank")
    token = security_manager.generate_token(user_id)
    return {"token": token, "user_id": user_id}


@app.get("/router/stats")
async def get_router_stats(api_key: str = Depends(verify_api_key)):
    if router is None:
        raise HTTPException(status_code=503, detail="Application is not initialized")
    return router.get_routing_stats()


@app.get("/")
async def root():
    return {
        "name": "Agent OS",
        "version": "1.0.0",
        "description": "Multi-agent system for specialized task execution",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=settings.FASTAPI_RELOAD)
