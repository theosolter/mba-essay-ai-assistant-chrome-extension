from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

async def error_handling_middleware(
    request: Request,
    call_next: Callable
) -> Any:
    try:
        return await call_next(request)
    except HTTPException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    except Exception as exc:
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"}
        )