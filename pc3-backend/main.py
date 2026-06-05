from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, initiatives, signatures, comments

app = FastAPI(
    title="Voz del Ciudadano",
    version="1.0.0",
    description="API para iniciativas legislativas ciudadanas",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Autenticacion"])
app.include_router(initiatives.router, prefix="/api/initiatives", tags=["Iniciativas"])
app.include_router(signatures.router, prefix="/api/initiatives", tags=["Firmas"])
app.include_router(comments.router, prefix="/api/initiatives", tags=["Comentarios"])


@app.get("/")
def root():
    return {"service": "Voz del Ciudadano", "version": "1.0.0"}
