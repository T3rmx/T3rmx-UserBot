from aiohttp import web


async def web_server():
    """Minimal HTTP app for platform health/bind checks (e.g. Railway PORT)."""

    async def _health(request):
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", _health)
    app.router.add_get("/health", _health)
    return app
