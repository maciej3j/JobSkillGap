from fastapi import FastAPI

from job_skill_gap.api.health_check import router as health_check_router


def create_application() -> FastAPI:
    app = FastAPI()
    app.include_router(health_check_router)
    return app


app = create_application()
