import os


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip()


def get_spot_mode() -> str:
    mode = _env_str("CCXT_SPOT_ENV", "").lower()
    if not mode:
        mode = "testnet" if _env_bool("CCXT_TESTNET", True) else "live"
    aliases = {
        "sandbox": "testnet",
        "test": "testnet",
        "prod": "live",
        "production": "live",
    }
    mode = aliases.get(mode, mode)
    if mode not in ("live", "testnet", "demo"):
        return "testnet"
    return mode


def account_source_label(exchange_id: str) -> str:
    mode = get_spot_mode()
    mode_label = {"live": "Live", "testnet": "Testnet", "demo": "Demo"}[mode]
    return f"{exchange_id.capitalize()} {mode_label} (CCXT)"


def apply_spot_mode(exchange) -> str:
    mode = get_spot_mode()
    if mode == "testnet":
        if hasattr(exchange, "set_sandbox_mode"):
            exchange.set_sandbox_mode(True)
        return mode

    # Ensure sandbox is disabled when not testnet mode
    if hasattr(exchange, "set_sandbox_mode"):
        try:
            exchange.set_sandbox_mode(False)
        except Exception:
            pass

    if mode == "demo":
        # Binance Spot Demo endpoint
        base = _env_str("CCXT_SPOT_DEMO_BASE_URL", "https://demo-api.binance.com").rstrip("/")
        if isinstance(getattr(exchange, "urls", {}).get("api"), dict):
            api_urls = exchange.urls["api"]
            api_urls["public"] = f"{base}/api/v3"
            api_urls["private"] = f"{base}/api/v3"
            api_urls["v1"] = f"{base}/api/v1"
            # Optional; harmless if endpoint not used by current calls.
            api_urls["sapi"] = f"{base}/sapi/v1"
            api_urls["sapiV2"] = f"{base}/sapi/v2"
            api_urls["sapiV3"] = f"{base}/sapi/v3"
            api_urls["sapiV4"] = f"{base}/sapi/v4"
    return mode


def create_spot_exchange(
    exchange_id: str,
    api_key: str = "",
    api_secret: str = "",
    api_password: str = "",
    require_credentials: bool = True,
):
    import ccxt

    if not hasattr(ccxt, exchange_id):
        raise RuntimeError(f"Exchange '{exchange_id}' tidak didukung ccxt.")
    if require_credentials and (not api_key or not api_secret):
        raise RuntimeError("CCXT_API_KEY/CCXT_API_SECRET belum terisi.")

    cls = getattr(ccxt, exchange_id)
    config = {
        "enableRateLimit": True,
        "timeout": 15000,
        "options": {
            "adjustForTimeDifference": False,
            "recvWindow": 10000,
            "fetchCurrencies": False,
            "fetchMarkets": {"types": ["spot"]},
            "fetchMargins": False,
        },
    }
    if api_key:
        config["apiKey"] = api_key
    if api_secret:
        config["secret"] = api_secret
    if api_password:
        config["password"] = api_password

    exchange = cls(config)
    apply_spot_mode(exchange)
    return exchange
