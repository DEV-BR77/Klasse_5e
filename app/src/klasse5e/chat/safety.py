import re

# Deliberately small and reviewable. It masks direct insults, while reports and
# human moderation remain necessary for context-dependent bullying.
_DIRECT_INSULTS = (
    "arschloch",
    "arschlöcher",
    "blöde kuh",
    "bloede kuh",
    "dumme kuh",
    "idiot",
    "idiotin",
    "vollidiot",
    "missgeburt",
    "hurensohn",
    "schlampe",
    "wichser",
    "fick dich",
)


def _mask(value):
    return value[0] + "•" * max(3, len(value) - 1)


def filter_chat_language(body):
    filtered = body
    hits = 0
    for phrase in sorted(_DIRECT_INSULTS, key=len, reverse=True):
        pattern = re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)

        def replace(match):
            nonlocal hits
            hits += 1
            return _mask(match.group(0))

        filtered = pattern.sub(replace, filtered)
    return filtered, hits
