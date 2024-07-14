from datetime import datetime
from typing import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.format_exc_info,
    structlog.processors.TimeStamper(fmt="iso", utc=False),
    structlog.processors.dict_tracebacks,
    structlog.processors.JSONRenderer(),
]

structlog.configure(
    processors,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """TODO."""

    def __init__(self, app: FastAPI) -> None:
        self._logger: structlog.BoundLogger = structlog.get_logger()
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """TODO."""
        path: str = request.url.path
        if request.query_params:
            path += f"?{request.query_params}"

        user_agent: str = request.headers.get("User-Agent", "UNKNOWN")

        request_id: str = str(uuid4())

        client = "TEST_CLIENT"
        if request.client is not None:
            client = f"{request.client.host}:{request.client.port}"

        log: structlog.BoundLogger = self._logger.bind(
            user_agent=user_agent,
            client=client,
            path=path,
            method=request.method,
            request_id=request_id,
            log_time=str(datetime.now()),
            security=False,
        )

        request.state.logger = log

        response = await call_next(request)

        status_code = response.status_code

        await request.state.logger.ainfo(
            "%s %s (%s)",
            request.method,
            path,
            status_code,
            complete_time=str(datetime.now()),
            status_code=status_code,
        )

        return response
