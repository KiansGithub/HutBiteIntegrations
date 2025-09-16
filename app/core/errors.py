from fastapi import FastAPI, Request 
from fastapi.responses import JSONResponse 
import httpx 

def install_error_handlers(app: FastAPI) -> None: 
    @app.exception_handler(httpx.HTTPStatusError)
    async def httpx_status_error_handler(request: Request, exc: httpx.HTTPStatusError): 
        try: 
            data = exc.response.json()
        except Exception: 
            data = {"detail": exc.response.text}
        return JSONResponse(
            status_code=exc.response.status_code, 
            content={"message": "HubRise API error", "detail": data},
        )