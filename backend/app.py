from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # importe le middleware CORS, qui permet au frontend (sur un autre domaine/port) de communiquer avec l'API.


from database import init_db #importe la fonction qui initialise la base de données SQLite (création des tables).
from routers import watches  #importe les modules de routes. watches gère le CRUD des montres

#crée l'instance de l'application avec un titre, une description et une version.
app = FastAPI(
    title="Watch API",
    description="API pédagogique FastAPI + SQL pur (sqlite3)",
    version="0.1.0",
)

#app.add_middleware(CORSMiddleware, ...) : autorise toutes les origines ("*"), méthodes et en-têtes. C'est pratique en développement car le frontend (ex. localhost:3000) peut appeler l'API (localhost:8000) sans blocage navigateur. En production, il faudrait restreindre allow_origins à l'URL réelle du frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()   # CREATE TABLE IF NOT EXISTS

# @app.get("/") est un décorateur qui dit à FastAPI :
#Quand un client HTTP envoie une requête GET à l'URL / (la racine du serveur), exécute la fonction juste en dessous."
#La fonction root() en dessous retourne un dictionnaire Python, que FastAPI convertit automatiquement en réponse JSON :
@app.get("/")
def root():
    return {"message": "Bienvenue sur WatchVault API"}


app.include_router(watches.router, prefix="/watch", tags=["Watches"])