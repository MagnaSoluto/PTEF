"""
Combinatorics module for efficient token counting.

Implements O(log N) algorithms for counting tokens and connectives
in numerical sequences up to N.
"""

from typing import Dict, Tuple
import math
from .grammar import text_number
from .lexicon import syllables


def count_tokens_up_to_999() -> Dict[str, int]:
    """
    Count all tokens in numbers 1-999.
    
    Returns:
        Dictionary mapping tokens to their total count
    """
    counts = {}
    
    for n in range(1, 1000):
        tokens = text_number(n)
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
    
    return counts


def count_tokens_up_to_N(N: int, policy: str = "R1") -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Count tokens and connectives up to N using O(log N) algorithm.
    
    Args:
        N: Maximum number to count up to
        policy: Grammar policy (currently only "R1" supported)
        
    Returns:
        Tuple of (token_counts, connective_counts)
    """
    if policy != "R1":
        raise ValueError("Only R1 policy is currently supported")
    
    if N <= 0:
        return {}, {}
    
    # For small N, use direct counting
    if N <= 1000:
        return _count_direct(N)
    
    # For large N, use block decomposition
    return _count_blocks(N)


def _count_direct(N: int) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Direct counting for small N."""
    token_counts = {}
    connective_counts = {}
    
    for n in range(1, N + 1):
        tokens = text_number(n)
        for i, token in enumerate(tokens):
            token_counts[token] = token_counts.get(token, 0) + 1
            
            # Count connectives (tokens that are "e")
            if token == "e":
                connective_counts["e"] = connective_counts.get("e", 0) + 1
    
    return token_counts, connective_counts


def _count_blocks(N: int) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Block-based counting for large N using O(log N) algorithm."""
    # Get base counts for 1-999
    base_tokens, base_connectives = count_tokens_up_to_999()
    
    # Initialize result counts
    token_counts = base_tokens.copy()
    connective_counts = base_connectives.copy()
    
    # Handle thousands
    if N >= 1000:
        thousands = N // 1000
        remainder = N % 1000
        
        # Count thousands blocks
        for _ in range(thousands):
            # Add "mil" token
            token_counts["mil"] = token_counts.get("mil", 0) + 1
            
            # Add all base tokens
            for token, count in base_tokens.items():
                token_counts[token] = token_counts.get(token, 0) + count
            
            # Add all base connectives
            for conn, count in base_connectives.items():
                connective_counts[conn] = connective_counts.get(conn, 0) + count
        
        # Handle remainder
        if remainder > 0:
            remainder_tokens = text_number(remainder)
            for token in remainder_tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
                if token == "e":
                    connective_counts["e"] = connective_counts.get("e", 0) + 1
    
    # Handle millions
    if N >= 1000000:
        millions = N // 1000000
        remainder = N % 1000000
        
        # Count millions blocks
        for _ in range(millions):
            # Add "milhão" or "milhões" token
            if millions == 1:
                token_counts["milhão"] = token_counts.get("milhão", 0) + 1
            else:
                token_counts["milhões"] = token_counts.get("milhões", 0) + 1
            
            # Add all base tokens
            for token, count in base_tokens.items():
                token_counts[token] = token_counts.get(token, 0) + count
        
        # Handle remainder
        if remainder > 0:
            remainder_tokens = text_number(remainder)
            for token in remainder_tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
                if token == "e":
                    connective_counts["e"] = connective_counts.get("e", 0) + 1
    
    return token_counts, connective_counts


def count_syllables_up_to_N(N: int, policy: str = "R1") -> int:
    """
    Count total syllables up to N.
    
    Args:
        N: Maximum number to count up to
        policy: Grammar policy
        
    Returns:
        Total syllable count
    """
    token_counts, _ = count_tokens_up_to_N(N, policy)
    
    total_syllables = 0
    for token, count in token_counts.items():
        try:
            token_syllables = syllables(token)
            total_syllables += token_syllables * count
        except KeyError:
            # Skip unknown tokens
            continue
    
    return total_syllables


def count_connectives_up_to_N(N: int, policy: str = "R1") -> int:
    """
    Count total connectives up to N.
    
    Args:
        N: Maximum number to count up to
        policy: Grammar policy
        
    Returns:
        Total connective count
    """
    _, connective_counts = count_tokens_up_to_N(N, policy)
    return sum(connective_counts.values())
