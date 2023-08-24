from fastapi import FastAPI
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette import status


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())},
    )
    logger.debug(f"Request validation exception: {response.body}")
    return response


def register_error_handling(app: FastAPI) -> None:
    app.add_exception_handler(ValidationError, request_validation_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
