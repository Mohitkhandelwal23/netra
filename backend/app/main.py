from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid

app = FastAPI(title="Netra Prototype API", version="0.1.0")

# CORS for quick prototyping
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
cameras: Dict[str, Dict] = {}
junctions: Dict[str, Dict] = {}
violations: Dict[str, Dict] = {}
challans: Dict[str, Dict] = {}
signal_states: Dict[str, Dict] = {}

# Models
class CameraCreate(BaseModel):
    junctionId: str
    name: str
    lat: float
    lon: float
    orientation: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    config: Optional[dict] = None

class Camera(CameraCreate):
    id: str
    lastSeen: Optional[datetime] = None

class ViolationCreate(BaseModel):
    cameraId: str
    timestamp: datetime
    type: str = Field(pattern="^(red_light|speeding|wrong_lane|pedestrian_encroachment)$")
    confidence: float = Field(ge=0, le=1)
    evidencePath: Optional[str] = None

class Violation(ViolationCreate):
    id: str
    status: str = "pending"
    issuedBy: Optional[str] = None

class ChallanCreate(BaseModel):
    violationId: str
    vehicleNumber: str
    fine: float
    notes: Optional[str] = None

class Challan(BaseModel):
    id: str
    violationId: str
    vehicleNumber: str
    fine: float
    issuedAt: Optional[datetime] = None
    dueDate: Optional[datetime] = None
    paidAt: Optional[datetime] = None
    paymentRef: Optional[str] = None
    status: str = "draft"

class SignalModeSet(BaseModel):
    mode: str = Field(pattern="^(ai|manual|scheduled)$")

class SignalPhaseSet(BaseModel):
    phase: str
    durationSeconds: int = Field(ge=5)

class SignalState(BaseModel):
    id: str
    junctionId: str
    phase: str
    startTime: datetime
    duration: int
    source: str
    operatorId: Optional[str] = None

# Sample bootstrap data
sample_junction_id = str(uuid.uuid4())
junctions[sample_junction_id] = {"id": sample_junction_id, "name": "MG Road x Residency Rd"}

sample_camera_id = str(uuid.uuid4())
cameras[sample_camera_id] = {
    "id": sample_camera_id,
    "junctionId": sample_junction_id,
    "name": "Cam-1",
    "lat": 12.9716,
    "lon": 77.5946,
    "resolution": "1920x1080",
    "fps": 25,
    "lastSeen": datetime.now(timezone.utc),
}

# Routes (subset of OpenAPI)
@app.get("/admin/cameras", response_model=List[Camera])
def list_cameras():
    return list(cameras.values())

@app.post("/admin/camera", status_code=201, response_model=Camera)
def create_camera(payload: CameraCreate):
    cam_id = str(uuid.uuid4())
    cam = payload.model_dump()
    cam.update({"id": cam_id, "lastSeen": None})
    cameras[cam_id] = cam
    return cam

@app.get("/challans/pending")
def get_pending_violations(limit: int = 50):
    items = [v for v in violations.values() if v.get("status") == "pending"]
    return {"items": items[:limit], "nextCursor": None}

@app.post("/challans/create", status_code=201, response_model=Challan)
def create_challan(payload: ChallanCreate):
    violation = violations.get(payload.violationId)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    challan_id = str(uuid.uuid4())
    challan = Challan(
        id=challan_id,
        violationId=payload.violationId,
        vehicleNumber=payload.vehicleNumber,
        fine=payload.fine,
        issuedAt=datetime.now(timezone.utc),
        status="issued",
    )
    challans[challan_id] = challan.model_dump()
    violation["status"] = "issued"
    return challan

@app.post("/signal/{junction}/mode")
def set_signal_mode(junction: str, payload: SignalModeSet):
    # store mode in signal state cache (simplified)
    st = signal_states.get(junction)
    if not st:
        st = {
            "id": str(uuid.uuid4()),
            "junctionId": junction,
            "phase": "R",
            "startTime": datetime.now(timezone.utc),
            "duration": 30,
            "source": payload.mode,
        }
    else:
        st["source"] = payload.mode
    signal_states[junction] = st
    return {"ok": True, "mode": payload.mode}

@app.post("/signal/{junction}/set-phase")
def set_phase(junction: str, payload: SignalPhaseSet):
    st = signal_states.get(junction)
    if not st:
        st = {
            "id": str(uuid.uuid4()),
            "junctionId": junction,
            "phase": payload.phase,
            "startTime": datetime.now(timezone.utc),
            "duration": payload.durationSeconds,
            "source": "manual",
        }
    else:
        st.update({
            "phase": payload.phase,
            "startTime": datetime.now(timezone.utc),
            "duration": payload.durationSeconds,
            "source": "manual",
        })
    signal_states[junction] = st
    return {"ok": True}

@app.get("/signal/{junction}/state", response_model=SignalState)
def get_signal_state(junction: str):
    st = signal_states.get(junction)
    if not st:
        # initialize default state
        st = {
            "id": str(uuid.uuid4()),
            "junctionId": junction,
            "phase": "R",
            "startTime": datetime.now(timezone.utc),
            "duration": 30,
            "source": "scheduled",
        }
        signal_states[junction] = st
    return st

@app.post("/ingest/edge-event", status_code=202)
def ingest_edge_event(event: dict):
    # For prototype, accept minimal payload and create pending violations if provided
    for v in event.get("violations", []) or []:
        vid = v.get("id") or str(uuid.uuid4())
        violation = {
            "id": vid,
            "cameraId": v.get("cameraId"),
            "timestamp": v.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "type": v.get("type", "red_light"),
            "evidencePath": v.get("evidencePath"),
            "confidence": v.get("confidence", 0.9),
            "status": "pending",
            "issuedBy": None,
        }
        violations[vid] = violation
    return {"accepted": True}

@app.get("/healthz")
def healthz():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}
