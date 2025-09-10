"""
Grammar module for generating Portuguese number words.

Implements the R1 policy for generating number words in Brazilian Portuguese
with proper "e" (and) connective rules.
"""

from typing import List


def text_number(n: int, policy: str = "R1") -> List[str]:
    """
    Generate Portuguese number words for numbers 1 to n.
    
    Args:
        n: Maximum number to generate words for
        policy: Grammar policy (currently only "R1" supported)
        
    Returns:
        List of tokens representing the number in Portuguese
        
    Raises:
        ValueError: If n is negative or policy is not supported
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if policy != "R1":
        raise ValueError("Only R1 policy is currently supported")
    
    if n == 0:
        return ["zero"]
    
    return _generate_tokens(n)


def _generate_tokens(n: int) -> List[str]:
    """Generate tokens for a given number."""
    if n == 0:
        return []
    
    # Handle special cases for 1-19
    if 1 <= n <= 19:
        return _units_tokens(n)
    
    # Handle 20-99
    if 20 <= n <= 99:
        return _tens_tokens(n)
    
    # Handle 100-199
    if 100 <= n <= 199:
        return _hundreds_tokens(n)
    
    # Handle 200-999
    if 200 <= n <= 999:
        return _hundreds_tokens(n)
    
    # Handle 1000-999999
    if 1000 <= n <= 999999:
        return _thousands_tokens(n)
    
    # Handle millions
    if 1000000 <= n <= 999999999:
        return _millions_tokens(n)
    
    # Handle billions
    if 1000000000 <= n <= 999999999999:
        return _billions_tokens(n)
    
    raise ValueError(f"Number {n} is too large for current implementation")


def _units_tokens(n: int) -> List[str]:
    """Generate tokens for units (1-19)."""
    units = [
        "", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove",
        "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", 
        "dezessete", "dezoito", "dezenove"
    ]
    return [units[n]] if units[n] else []


def _tens_tokens(n: int) -> List[str]:
    """Generate tokens for tens (20-99)."""
    tens = ["", "", "vinte", "trinta", "quarenta", "cinquenta", 
            "sessenta", "setenta", "oitenta", "noventa"]
    
    tens_digit = n // 10
    units_digit = n % 10
    
    tokens = [tens[tens_digit]]
    
    if units_digit > 0:
        tokens.extend(["e", _units_tokens(units_digit)[0]])
    
    return tokens


def _hundreds_tokens(n: int) -> List[str]:
    """Generate tokens for hundreds (100-999)."""
    hundreds_digit = n // 100
    remainder = n % 100
    
    if n == 100:
        return ["cem"]
    
    if hundreds_digit == 1:
        tokens = ["cento"]
    else:
        hundreds_words = ["", "", "duzentos", "trezentos", "quatrocentos", 
                         "quinhentos", "seiscentos", "setecentos", 
                         "oitocentos", "novecentos"]
        tokens = [hundreds_words[hundreds_digit]]
    
    if remainder > 0:
        if remainder < 20:
            tokens.extend(["e"] + _units_tokens(remainder))
        else:
            tens_tokens = _tens_tokens(remainder)
            if tens_tokens:
                tokens.extend(["e"] + tens_tokens)
    
    return tokens


def _thousands_tokens(n: int) -> List[str]:
    """Generate tokens for thousands (1000-999999)."""
    thousands = n // 1000
    remainder = n % 1000
    
    tokens = []
    
    if thousands == 1:
        tokens.append("mil")
    else:
        thousands_tokens = _generate_tokens(thousands)
        tokens.extend(thousands_tokens)
        tokens.append("mil")
    
    if remainder > 0:
        if remainder < 100:
            tokens.extend(["e"] + _generate_tokens(remainder))
        else:
            remainder_tokens = _generate_tokens(remainder)
            if remainder_tokens:
                tokens.extend(["e"] + remainder_tokens)
    
    return tokens


def _millions_tokens(n: int) -> List[str]:
    """Generate tokens for millions (1000000-999999999)."""
    millions = n // 1000000
    remainder = n % 1000000
    
    tokens = []
    
    if millions == 1:
        tokens.append("um")
        tokens.append("milhão")
    else:
        millions_tokens = _generate_tokens(millions)
        tokens.extend(millions_tokens)
        tokens.append("milhões")
    
    if remainder > 0:
        if remainder < 100:
            tokens.extend(["e"] + _generate_tokens(remainder))
        else:
            remainder_tokens = _generate_tokens(remainder)
            if remainder_tokens:
                tokens.extend(["e"] + remainder_tokens)
    
    return tokens


def _billions_tokens(n: int) -> List[str]:
    """Generate tokens for billions (1000000000-999999999999)."""
    billions = n // 1000000000
    remainder = n % 1000000000
    
    tokens = []
    
    if billions == 1:
        tokens.append("um")
        tokens.append("bilhão")
    else:
        billions_tokens = _generate_tokens(billions)
        tokens.extend(billions_tokens)
        tokens.append("bilhões")
    
    if remainder > 0:
        if remainder < 100:
            tokens.extend(["e"] + _generate_tokens(remainder))
        else:
            remainder_tokens = _generate_tokens(remainder)
            if remainder_tokens:
                tokens.extend(["e"] + remainder_tokens)
    
    return tokens
