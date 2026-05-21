"""Main FastAPI application"""
import logging
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

from config import settings
from core.llm import get_llm_provider
from core.router import AgentRouter
from core.security import security_manager
from agents import ResearchAgent, CodingAgent, AutomationAgent, MarketingAgent

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agent OS",
    description="Multi-agent system for specialized task execution",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
router = None
agents = {}
llm_provider = None


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global router, agents, llm_provider
    
    logger.info(f"Starting Agent OS in {settings.FASTAPI_ENV} mode")
    
    try:
        # Initialize LLM provider
        if settings.OPENAI_API_KEY:
            llm_provider = get_llm_provider("openai", settings.OPENAI_API_KEY)
            logger.info("Using OpenAI as LLM provider")
        elif settings.ANTHROPIC_API_KEY:
            llm_provider = get_llm_provider("anthropic", settings.ANTHROPIC_API_KEY)
            logger.info("Using Anthropic as LLM provider")
        elif settings.GOOGLE_API_KEY:
            llm_provider = get_llm_provider("google", settings.GOOGLE_API_KEY)
            logger.info("Using Google as LLM provider")
        else:
            raise ValueError("No LLM API key configured")
        
        # Initialize router
        router = AgentRouter()
        logger.info("Agent router initialized")
        
        # Initialize agents
        agents = {
            "research": ResearchAgent(llm_provider),
            "coding": CodingAgent(llm_provider),
            "automation": AutomationAgent(llm_provider),
            "marketing": MarketingAgent(llm_provider),
        }
        logger.info(f"Initialized {len(agents)} agents")
        
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Agent OS")


# Request/Response models
class TaskRequest(BaseModel):
    """Task execution request"""
    task: str
    agent_type: Optional[str] = None


class TaskResponse(BaseModel):
    """Task execution response"""
    task: str
    agent_type: str
    result: str
    status: str


class AgentInfo(BaseModel):
    """Agent information"""
    name: str
    description: str
    status: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    environment: str
    agents_available: int


# Helper function for API key verification
def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Verify API key from header"""
    if not x_api_key:
        raise HTTPException(status_code=403, detail="API key required")
    if not security_manager.verify_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        environment=settings.FASTAPI_ENV,
        agents_available=len(agents)
    )


@app.get("/agents", response_model=list)
async def list_agents(api_key: str = Depends(verify_api_key)):
    """List available agents"""
    agent_info = []
    for name, agent in agents.items():
        agent_info.append({
            "name": agent.name,
            "description": router.get_agent_description(name),
            "status": "active"
        })
    return agent_info


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest, api_key: str = Depends(verify_api_key)):
    """Execute a task"""
    try:
        # Route the task
        routing_result = router.route_task(request.task, request.agent_type)
        agent_type = routing_result["agent_type"]
        
        # Get the agent
        if agent_type not in agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        agent = agents[agent_type]
        
        # Execute the task
        logger.info(f"Executing task with {agent_type} agent: {request.task}")
        result = await agent.execute(request.task)
        
        logger.info(f"Task completed with {agent_type} agent")
        return TaskResponse(
            task=request.task,
            agent_type=agent_type,
            result=result,
            status="completed"
        )
    except Exception as e:
        logger.error(f"Task execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agent/{agent_type}/info")
async def get_agent_info(agent_type: str, api_key: str = Depends(verify_api_key)):
    """Get information about a specific agent"""
    if agent_type not in agents:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_type}")
    
    agent = agents[agent_type]
    return agent.get_agent_info()


@app.post("/token")
async def generate_token(user_id: str, api_key: str = Depends(verify_api_key)):
    """Generate access token"""
    token = security_manager.generate_token(user_id)
    return {"token": token, "user_id": user_id}


@app.get("/router/stats")
async def get_router_stats(api_key: str = Depends(verify_api_key)):
    """Get router statistics"""
    return router.get_routing_stats()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Agent OS",
        "version": "1.0.0",
        "description": "Multi-agent system for specialized task execution",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.FASTAPI_RELOAD
    )