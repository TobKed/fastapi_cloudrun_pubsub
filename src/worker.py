from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from loguru import logger

app = FastAPI()


@app.post("/pubsub", status_code=status.HTTP_204_NO_CONTENT)
async def pubsub(request: Request) -> None:
    body = await request.body()
    logger.info(f"Request from PubSub: {body}")


@app.post("/pubsub_dlq", status_code=status.HTTP_204_NO_CONTENT)
async def pubsub_dlq(request: Request) -> None:
    body = await request.body()
    logger.info(f"Request from PubSub DLQ: {body}")
