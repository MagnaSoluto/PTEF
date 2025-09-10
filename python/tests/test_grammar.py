"""
Tests for grammar module.
"""

import pytest
from ptef.grammar import text_number


def test_text_number_basic():
    """Test basic number word generation."""
    assert text_number(1) == ["um"]
    assert text_number(2) == ["dois"]
    assert text_number(3) == ["três"]
    assert text_number(10) == ["dez"]
    assert text_number(11) == ["onze"]


def test_text_number_tens():
    """Test tens (20-99)."""
    assert text_number(20) == ["vinte"]
    assert text_number(21) == ["vinte", "e", "um"]
    assert text_number(30) == ["trinta"]
    assert text_number(31) == ["trinta", "e", "um"]


def test_text_number_hundreds():
    """Test hundreds (100-999)."""
    assert text_number(100) == ["cem"]
    assert text_number(101) == ["cento", "e", "um"]
    assert text_number(200) == ["duzentos"]
    assert text_number(201) == ["duzentos", "e", "um"]
    assert text_number(999) == ["novecentos", "e", "noventa", "e", "nove"]


def test_text_number_thousands():
    """Test thousands (1000-999999)."""
    assert text_number(1000) == ["mil"]
    assert text_number(1001) == ["mil", "e", "um"]
    assert text_number(2000) == ["dois", "mil"]
    assert text_number(2001) == ["dois", "mil", "e", "um"]


def test_text_number_millions():
    """Test millions."""
    assert text_number(1000000) == ["um", "milhão"]
    assert text_number(2000000) == ["dois", "milhões"]


def test_text_number_edge_cases():
    """Test edge cases."""
    assert text_number(0) == ["zero"]
    
    with pytest.raises(ValueError):
        text_number(-1)
    
    with pytest.raises(ValueError):
        text_number(1, policy="invalid")


def test_text_number_connectives():
    """Test that connectives are properly placed."""
    # Test "e" connective in various positions
    result = text_number(21)
    assert "e" in result
    assert result.index("e") == 1  # "e" should be between tens and units
    
    result = text_number(101)
    assert "e" in result
    assert result.index("e") == 1  # "e" should be between hundreds and units


def test_text_number_consistency():
    """Test consistency of number word generation."""
    # Test that the same number always generates the same tokens
    for n in range(1, 100):
        result1 = text_number(n)
        result2 = text_number(n)
        assert result1 == result2


def test_text_number_policy():
    """Test policy parameter."""
    # Currently only R1 is supported
    assert text_number(21, policy="R1") == ["vinte", "e", "um"]
    
    with pytest.raises(ValueError):
        text_number(21, policy="R2")
