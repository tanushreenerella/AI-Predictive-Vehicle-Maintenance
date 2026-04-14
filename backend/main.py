from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.vehicles import router as vehicle_router
from backend.routes.analysis import router as analysis_router
from backend.models.vehicle import Vehicle
from backend.base import Base
from backend.session import engine
from backend.routes.dashboard import router as dashboard_router
from backend.routes.vehicle_health import router as vehicle_health_router
from backend.routes.alerts import router as alerts_router
from backend.routes.auth import router as auth_router
from backend.routes.scheduling import router as scheduling_router
from backend.routes.agent_chat import router as agent_chat_router
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Predictive Maintenance API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Backend running"}

app.include_router(vehicle_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)
app.include_router(vehicle_health_router)
app.include_router(alerts_router)
app.include_router(auth_router)
app.include_router(scheduling_router)
app.include_router(agent_chat_router)


