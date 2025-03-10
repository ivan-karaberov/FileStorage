import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router as api_router
from exceptions.exceptions import APIException
from config import settings

settings.logger.configure_logging()

app = FastAPI()


@app.exception_handler(APIException)
async def custom_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", port=3001, reload=True)
