import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RatesUnavailable(Exception):
    pass


async def get_rate(base: str, target: str) -> float:
    if base.upper() == target.upper():
        return 1.0

    url = f"{settings.rates_api_url}/latest"
    params = {"base": base.upper(), "symbols": target.upper()}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        logger.warning("rate service failed: %s", exc)
        raise RatesUnavailable("Rate service se jawab nahi mila") from exc

    rate = data.get("rates", {}).get(target.upper())
    if rate is None:
        raise RatesUnavailable(f"{target} ka rate nahi mila")

    return float(rate)
