from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger as LOGGER

from app.routers.mailer import router
from app.settings import SETTINGS


broker = RabbitBroker(SETTINGS.RABBITMQ_URL)

broker.include_router(router)

app = FastStream(broker)


@app.after_startup
async def startup() -> None:
    SETTINGS.configure_logging()
    LOGGER.info("[MAILER] Service started")
