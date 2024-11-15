import logging
from contextlib import asynccontextmanager

from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from .site.router import router as site_router
from .bot.create_bot import dp, start_bot, stop_bot, bot
from .config import settings
from .database import engine
from .bot.router import router as bot_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting bot setup...")

    logging.info("Creating database...")
    await engine.create_db()

    dp.include_router(bot_router)
    await start_bot()
    webhook_url = settings.get_webhook_url()
    await bot.set_webhook(url=webhook_url,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    logging.info(f"Webhook set to {webhook_url}")
    yield
    logging.info("Shutting down bot...")
    await bot.delete_webhook()
    await stop_bot()
    logging.info("Webhook deleted")

    # logging.info("Dropping database...")
    # await engine.drop_db()

app = FastAPI(lifespan=lifespan)


app.mount('/static', StaticFiles(directory='app/static'), 'static')


@app.post("/webhook")
async def webhook(request: Request) -> None:
    logging.info("Received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    logging.info("Update processed")


app.include_router(site_router)