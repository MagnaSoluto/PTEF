"""
Tests for lexicon module.
"""

import pytest
from ptef.lexicon import syllables, get_available_tokens, validate_tokens


def test_syllables_basic():
    """Test basic syllable counting."""
    assert syllables("um") == 1
    assert syllables("dois") == 1
    assert syllables("três") == 1
    assert syllables("quatro") == 2
    assert syllables("cinco") == 2


def test_syllables_connectives():
    """Test syllable counting for connectives."""
    assert syllables("e") == 1


def test_syllables_hundreds():
    """Test syllable counting for hundreds."""
    assert syllables("cem") == 1
    assert syllables("cento") == 2
    assert syllables("duzentos") == 3
    assert syllables("quatrocentos") == 4


def test_syllables_thousands():
    """Test syllable counting for thousands."""
    assert syllables("mil") == 1
    assert syllables("milhão") == 2
    assert syllables("milhões") == 2


def test_syllables_unknown_token():
    """Test handling of unknown tokens."""
    with pytest.raises(KeyError):
        syllables("unknown_token")


def test_get_available_tokens():
    """Test getting available tokens."""
    tokens = get_available_tokens()
    
    # Check that basic tokens are available
    assert "um" in tokens
    assert "dois" in tokens
    assert "e" in tokens
    assert "mil" in tokens
    
    # Check that it returns a set
    assert isinstance(tokens, set)


def test_validate_tokens():
    """Test token validation."""
    # Test with valid tokens
    valid_tokens = {"um", "dois", "e", "mil"}
    validation = validate_tokens(valid_tokens)
    
    for token in valid_tokens:
        assert validation[token] is True
    
    # Test with invalid tokens
    invalid_tokens = {"um", "unknown_token", "e"}
    validation = validate_tokens(invalid_tokens)
    
    assert validation["um"] is True
    assert validation["e"] is True
    assert validation["unknown_token"] is False


def test_lexicon_consistency():
    """Test that lexicon is consistent."""
    # Test that the same token always returns the same syllable count
    for token in ["um", "dois", "três", "quatro", "cinco"]:
        count1 = syllables(token)
        count2 = syllables(token)
        assert count1 == count2


def test_lexicon_coverage():
    """Test that lexicon covers all generated tokens."""
    from ptef.grammar import text_number
    
    # Generate tokens for numbers 1-100
    all_tokens = set()
    for n in range(1, 101):
        tokens = text_number(n)
        all_tokens.update(tokens)
    
    # Validate that all tokens are in lexicon
    validation = validate_tokens(all_tokens)
    
    # All tokens should be valid
    for token, is_valid in validation.items():
        assert is_valid, f"Token '{token}' not found in lexicon"
