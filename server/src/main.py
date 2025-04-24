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
            "http://localhost:8000",  # Common frontend port
            "http://127.0.0.1:8000",  # Alternative localhost
            "http://localhost:3000",  # Common React/Vue port
            "http://127.0.0.1:3000",  # Alternative localhost
            "http://localhost:8080",  # Common alternative port
            "http://127.0.0.1:8080",  # Alternative localhost
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
