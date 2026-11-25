import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("velmora")


class ValidationError(ValueError):
    pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            {"location": error["loc"], "message": error["msg"]}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={"detail": "Solicitud inválida", "errors": errors},
        )

    @app.exception_handler(ValidationError)
    async def domain_validation_handler(
        _request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, _exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "Error no controlado al procesar %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"},
        )
