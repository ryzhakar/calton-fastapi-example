from enum import IntEnum


# UPPERCASE_ENUMS are unpythonic, hence lovercase enums.
# Ultimately, that's a matter of taste.
class SentimentEnum(IntEnum):
    """Int-based enumeration of text sentiments."""
    positive = 1
    negative = 0
    neutral = -1
