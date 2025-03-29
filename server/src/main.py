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
        ],  # Allows all origins (replace with specific origins as needed)
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods
        allow_headers=["*"],  # Allows all headers
    )

    @app.get("/user")
    def get_user(user_id: int, con: sqlite3.Connection = Depends(db.get_db)):
        return db.get_user_info(con, user_id)

    app.include_router(api.user_router)

    uvicorn.run(app, host="0.0.0.0", port=3000)


if __name__ == "__main__":
    main()
