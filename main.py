from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from auth_routes import router as auth_router
from task_routes import router as task_router
from sub_agent_routes import router as sub_agent_router
from skill_routes import router as skill_router

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://todo-frontend-eight-wheat.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(sub_agent_router)
app.include_router(skill_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}