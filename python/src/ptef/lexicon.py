"""
Lexicon module for syllable counting.

Loads the Brazilian Portuguese number lexicon and provides syllable counting
functionality.
"""

import os
import pandas as pd
from typing import Dict, Set


# Global lexicon cache
_lexicon: Dict[str, int] = {}
_loaded = False


def load_lexicon() -> Dict[str, int]:
    """
    Load the Brazilian Portuguese number lexicon.
    
    Returns:
        Dictionary mapping tokens to syllable counts
    """
    global _lexicon, _loaded
    
    if _loaded:
        return _lexicon
    
    # Get the directory of this module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the lexicon file
    lexicon_path = os.path.join(
        current_dir, "..", "..", "..", "..", "data", "lexicon", 
        "bp_number_tokens_syllables.csv"
    )
    
    try:
        df = pd.read_csv(lexicon_path)
        _lexicon = dict(zip(df['token'], df['syllables']))
        _loaded = True
    except FileNotFoundError:
        # Fallback to a minimal lexicon if file not found
        _lexicon = {
            "um": 1, "dois": 1, "três": 1, "quatro": 2, "cinco": 2,
            "seis": 1, "sete": 2, "oito": 2, "nove": 2, "dez": 1,
            "onze": 2, "doze": 2, "treze": 2, "quatorze": 3, "quinze": 2,
            "dezesseis": 4, "dezessete": 4, "dezoito": 3, "dezenove": 4,
            "vinte": 2, "trinta": 2, "quarenta": 3, "cinquenta": 3,
            "sessenta": 3, "setenta": 3, "oitenta": 3, "noventa": 3,
            "cem": 1, "cento": 2, "duzentos": 3, "trezentos": 3,
            "quatrocentos": 4, "quinhentos": 3, "seiscentos": 3,
            "setecentos": 4, "oitocentos": 4, "novecentos": 4,
            "mil": 1, "milhão": 2, "milhões": 2, "e": 1
        }
        _loaded = True
    
    return _lexicon


def syllables(token: str) -> int:
    """
    Get the syllable count for a given token.
    
    Args:
        token: The token to count syllables for
        
    Returns:
        Number of syllables in the token
        
    Raises:
        KeyError: If token is not found in lexicon
    """
    lexicon = load_lexicon()
    
    if token not in lexicon:
        raise KeyError(f"Token '{token}' not found in lexicon")
    
    return lexicon[token]


def get_available_tokens() -> Set[str]:
    """
    Get the set of all available tokens in the lexicon.
    
    Returns:
        Set of all tokens in the lexicon
    """
    lexicon = load_lexicon()
    return set(lexicon.keys())


def validate_tokens(tokens: Set[str]) -> Dict[str, bool]:
    """
    Validate that all tokens exist in the lexicon.
    
    Args:
        tokens: Set of tokens to validate
        
    Returns:
        Dictionary mapping tokens to validation status
    """
    available = get_available_tokens()
    return {token: token in available for token in tokens}
