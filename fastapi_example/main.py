import uvicorn
import argparse
from fastapi import FastAPI
from sys import exit
from fastapi_example.config import settings
from fastapi_example.routes import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/healthcheck/")
def healthcheck():
    return {"status": "OK"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Learn FastAPI framework")
    parser.add_argument("--reload",
                        dest="reload",
                        action="store_true",
                        help="Activate application reload.")
    parser.add_argument("--debug",
                        dest="debug",
                        action="store_true",
                        help="Show detailed print information")
    arguments = parser.parse_args()
    exit(uvicorn.run("main:app", host="0.0.0.0",
                     port=settings.port,
                     log_level="debug" if arguments.debug else "info",
                     reload=arguments.reload))
