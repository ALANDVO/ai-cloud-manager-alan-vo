import time, logging
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        logger.info("%s %s %.0fms %d", request.method, request.url.path, elapsed, response.status_code)
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.rpm = requests_per_minute
        self.buckets = {}

    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self.buckets.get(key, [])
        bucket = [t for t in bucket if now - t < 60]
        if len(bucket) >= self.rpm:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        bucket.append(now)
        self.buckets[key] = bucket
        return await call_next(request)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})
