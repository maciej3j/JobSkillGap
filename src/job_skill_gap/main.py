from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from job_skill_gap.db import get_db

app = FastAPI()


@app.get("/health_check")
async def health_check(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {
        "status": "OK",
    }
