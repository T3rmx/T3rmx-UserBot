try:
    import randomstuff
except Exception:
    randomstuff = None

from ..Config import Config

rs_client = None
try:
    if getattr(Config, "RANDOM_STUFF_API_KEY", None) and randomstuff is not None:
        rs_client = randomstuff.AsyncClient(api_key=Config.RANDOM_STUFF_API_KEY, version="4")
except Exception:
    rs_client = None
