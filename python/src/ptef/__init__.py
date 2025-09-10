"""
PTEF - Pronunciation-Time Estimation Framework for Brazilian Portuguese

A probabilistic framework for estimating pronunciation time of numerical sequences
in Brazilian Portuguese.
"""

from .ptef import estimate, PTEFParams
from .grammar import text_number
from .lexicon import syllables
from .combinatorics import count_tokens_up_to_N
from .duration import expected_syllable_duration, variance_syllable_duration
from .pauses import count_pauses

__version__ = "0.1.0"
__author__ = "PTEF Team"
__email__ = "ptef@example.com"

__all__ = [
    "estimate",
    "PTEFParams", 
    "text_number",
    "syllables",
    "count_tokens_up_to_N",
    "expected_syllable_duration",
    "variance_syllable_duration",
    "count_pauses",
]
