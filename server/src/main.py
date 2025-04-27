import sqlite3
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import db
import api

def main():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api.user_router)
    app.include_router(api.classes_router)

    uvicorn.run(app, host="0.0.0.0", port=3003)


if __name__ == "__main__":
    main()
