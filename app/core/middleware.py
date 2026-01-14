from fastapi import Request
import time
import uuid
from app.utils.logger import logger

async def add_process_time_header(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response

async def add_request_id_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(f"Request ID: {request_id}: {request.method} {request.url}")
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response
