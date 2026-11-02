from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by the connecting IP (request.client.host). Counts are kept in this
# process's memory: they reset on restart and are not shared between workers.
# key_style="endpoint" buckets by handler function rather than URL, so path
# aliases of one handler (/chat and /agent/chat) share a single limit.
limiter = Limiter(key_func=get_remote_address, key_style="endpoint")

AUTH_LIMIT = "5/minute"
EXPENSIVE_LIMIT = "10/minute"
