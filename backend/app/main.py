from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth
from app.api.endpoints import notes
from app.api.endpoints import todos
from app.api.endpoints import organizations

app = FastAPI(title="Full Stack App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(todos.router, prefix="/todos", tags=["todos"])
app.include_router(organizations.router, prefix="/organizations", tags=["organizations"])

@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}