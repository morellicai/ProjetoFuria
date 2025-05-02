from fastapi import Request, HTTPException
from typing import List, Callable
import logging

class FileUploadMiddleware:
    def __init__(
        self,
        max_size: int = 1024 * 1024 * 2, # 2MB
        upload_routes: List[str] = None
    ):
        self.max_size = max_size
        self.upload_routes = upload_routes or ["/upload"]
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("upload_middleware")

    async def __call__(self, request: Request, call_next: Callable):
        if request.method == "POST" and request.url.path in self.upload_routes:
            if "content-length" not in request.headers:
                raise HTTPException(
                    status_code=411,
                    detail="Content-Length header não encontrado"
                )

            content_length = int(request.headers["content-length"])

            if content_length > self.max_size:
                self.logger.warning(f"Upload rejeitado: {content_length/1024/1024:.1f}MB (max: {self.max_size/1024/1024:.1f}MB)")
                raise HTTPException(
                    status_code=413,
                    detail=f"File size exceeds the maximum allowed size of {self.max_size/1024/1024:.1f}MB"
                )

            self.logger.info(f"Upload permitido: {content_length/1024/1024:.1f}MB")

        response = await call_next(request)
        return response