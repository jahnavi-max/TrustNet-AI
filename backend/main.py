from typing import Any, Literal
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database as db
import policy_engine
import validator

# Import email trust services
from services.email_service import EmailService
from services.analysis_service import ContentAnalysisService

# Initialize single FastAPI instance
app = FastAPI(title="TrustNet AI")

# Configure CORS for React frontend (Vite & CRA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
db.init()

REDUNDANT_WINDOW = 60  # seconds
RELIABILITY = {
    "None": 98,
    "Redundant Call": 65,
    "Invalid Parameter": 41,
    "Policy Violation": 35,
    "Unauthorized Action": 32,
}

# --- Request Schemas ---

class AgentRequest(BaseModel):
    role: Literal["Admin", "Teacher", "Viewer"]
    tool: str
    action: str
    params: dict[str, Any] = {}

class EmailVerifyRequest(BaseModel):
    email: str

class ContentAnalyzeRequest(BaseModel):
    sender: str
    subject: str
    body: str

# --- Agent Guardrail Core Logic ---

def decide(r: AgentRequest):
    """Run the four checks in order; return (decision, risk_type, rule, explanation)."""
    p = policy_engine.violated(r.role, r.tool, r.params, "Unauthorized Action")
    if p:
        return "Block", "Unauthorized Action", p["id"], p["message"].format(role=r.role)
    
    err = validator.validate(r.tool, r.params)
    if err:
        return "Block", "Invalid Parameter", "VAL-001", f"Invalid parameters: {err}."
    
    p = policy_engine.violated(r.role, r.tool, r.params, "Policy Violation")
    if p:
        return "Block", "Policy Violation", p["id"], p["message"].format(role=r.role)
    
    if db.is_duplicate(r.role, r.tool, r.action, r.params, REDUNDANT_WINDOW):
        return (
            "Warn",
            "Redundant Call",
            "RED-001",
            f"The same request was already executed in the last {REDUNDANT_WINDOW}s, so it was not run again.",
        )
    return "Allow", "None", "-", "Request passed all guardrail checks."

# --- Agent Guardrail Endpoints ---

@app.post("/evaluate")
def evaluate(r: AgentRequest):
    decision, risk, rule, why = decide(r)
    score = RELIABILITY[risk]
    db.add_log(r.role, r.tool, r.action, r.params, decision, risk, rule, why, score)
    return {"decision": decision, "risk_type": risk, "rule": rule, "explanation": why, "reliability": score}

@app.get("/stats")
def stats():
    return db.stats()

@app.get("/logs")
def logs():
    return db.recent_logs()

@app.get("/health")
def health():
    return {"status": "ok", "policies": db.policy_count(), "validation": len(validator.SCHEMAS) > 0}

# --- Email Trust Engine Endpoints ---

email_trust_router = APIRouter(prefix="/api/email-trust", tags=["Email Trust Engine"])

@email_trust_router.post("/verify-address")
async def verify_address_endpoint(payload: EmailVerifyRequest):
    try:
        return await EmailService.verify_address(payload.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@email_trust_router.post("/analyze-content")
async def analyze_content_endpoint(payload: ContentAnalyzeRequest):
    try:
        return await ContentAnalysisService.analyze_content(payload.sender, payload.subject, payload.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(email_trust_router)