import contextvars

IS_TRUSTED_NODE = contextvars.ContextVar("IS_AUTHORITY_NODE", default=False)
MY_UUID = contextvars.ContextVar("MY_UUID", default=None)

KNOWN_MINERS_LIST = contextvars.ContextVar("KNOWN_MINERS_LIST", default=[])
