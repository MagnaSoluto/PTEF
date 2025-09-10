"""
Tests for combinatorics module.
"""

import pytest
from ptef.combinatorics import (
    count_tokens_up_to_999,
    count_tokens_up_to_N,
    count_syllables_up_to_N,
    count_connectives_up_to_N
)


def test_count_tokens_up_to_999():
    """Test token counting for 1-999."""
    counts = count_tokens_up_to_999()
    
    # Check that basic tokens are present
    assert "um" in counts
    assert "dois" in counts
    assert "e" in counts
    assert "mil" in counts
    
    # Check that counts are positive
    for token, count in counts.items():
        assert count > 0
    
    # Check that "um" appears at least once
    assert counts["um"] >= 1


def test_count_tokens_up_to_N_small():
    """Test token counting for small N."""
    # Test N=10
    token_counts, connective_counts = count_tokens_up_to_N(10)
    
    # Check that we have some tokens
    assert len(token_counts) > 0
    assert len(connective_counts) > 0
    
    # Check that "um" appears once
    assert token_counts["um"] == 1
    
    # Check that "e" appears in connectives
    assert "e" in connective_counts


def test_count_tokens_up_to_N_medium():
    """Test token counting for medium N."""
    # Test N=100
    token_counts, connective_counts = count_tokens_up_to_N(100)
    
    # Check that we have more tokens than for N=10
    assert len(token_counts) > 0
    assert len(connective_counts) > 0
    
    # Check that "um" appears multiple times
    assert token_counts["um"] > 1


def test_count_tokens_up_to_N_large():
    """Test token counting for large N."""
    # Test N=1000
    token_counts, connective_counts = count_tokens_up_to_N(1000)
    
    # Check that we have tokens
    assert len(token_counts) > 0
    assert len(connective_counts) > 0
    
    # Check that "mil" appears
    assert "mil" in token_counts


def test_count_tokens_consistency():
    """Test consistency between direct and fast counting."""
    # For small N, fast counting should match direct counting
    for N in [10, 50, 100]:
        fast_counts, fast_conn = count_tokens_up_to_N(N)
        
        # Direct counting
        direct_counts = {}
        direct_conn = {}
        for n in range(1, N + 1):
            from ptef.grammar import text_number
            tokens = text_number(n)
            for token in tokens:
                direct_counts[token] = direct_counts.get(token, 0) + 1
                if token == "e":
                    direct_conn[token] = direct_conn.get(token, 0) + 1
        
        # Compare counts
        all_tokens = set(fast_counts.keys()) | set(direct_counts.keys())
        for token in all_tokens:
            fast_count = fast_counts.get(token, 0)
            direct_count = direct_counts.get(token, 0)
            assert fast_count == direct_count, f"Token '{token}' count mismatch: fast={fast_count}, direct={direct_count}"


def test_count_syllables_up_to_N():
    """Test syllable counting up to N."""
    # Test N=10
    syllables = count_syllables_up_to_N(10)
    assert syllables > 0
    
    # Test N=100
    syllables_100 = count_syllables_up_to_N(100)
    assert syllables_100 > syllables  # Should be more syllables for larger N


def test_count_connectives_up_to_N():
    """Test connective counting up to N."""
    # Test N=10
    connectives = count_connectives_up_to_N(10)
    assert connectives >= 0
    
    # Test N=100
    connectives_100 = count_connectives_up_to_N(100)
    assert connectives_100 >= connectives  # Should be more or equal connectives for larger N


def test_count_tokens_policy():
    """Test policy parameter."""
    # Currently only R1 is supported
    counts, _ = count_tokens_up_to_N(10, policy="R1")
    assert len(counts) > 0
    
    with pytest.raises(ValueError):
        count_tokens_up_to_N(10, policy="R2")


def test_count_tokens_edge_cases():
    """Test edge cases for token counting."""
    # Test N=0
    counts, conn = count_tokens_up_to_N(0)
    assert len(counts) == 0
    assert len(conn) == 0
    
    # Test N=1
    counts, conn = count_tokens_up_to_N(1)
    assert counts["um"] == 1
    assert len(conn) == 0  # No connectives for single number


def test_count_tokens_scaling():
    """Test that token counting scales properly."""
    # Test that counts increase with N
    counts_10, _ = count_tokens_up_to_N(10)
    counts_100, _ = count_tokens_up_to_N(100)
    
    # Total token count should increase
    total_10 = sum(counts_10.values())
    total_100 = sum(counts_100.values())
    assert total_100 > total_10
