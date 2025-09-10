"""
Tests for duration module.
"""

import pytest
import math
from ptef.duration import (
    DurationParams,
    expected_syllable_duration,
    variance_syllable_duration,
    expected_duration_for_syllables,
    variance_duration_for_syllables,
    get_default_params,
    create_params
)


def test_duration_params():
    """Test DurationParams model."""
    params = DurationParams()
    
    # Check default values
    assert params.mu == 0.15
    assert params.sigma == 0.3
    assert params.speaker_effect == 1.0
    assert params.fatigue_coeff == 0.0


def test_expected_syllable_duration():
    """Test expected syllable duration calculation."""
    params = DurationParams()
    duration = expected_syllable_duration(params)
    
    # Should be positive
    assert duration > 0
    
    # Should be approximately exp(mu + sigma^2/2) * speaker_effect
    expected = math.exp(params.mu + (params.sigma**2) / 2) * params.speaker_effect
    assert abs(duration - expected) < 1e-10


def test_variance_syllable_duration():
    """Test variance of syllable duration calculation."""
    params = DurationParams()
    variance = variance_syllable_duration(params)
    
    # Should be positive
    assert variance > 0
    
    # Should be approximately exp(2*mu + sigma^2) * (exp(sigma^2) - 1) * speaker_effect^2
    expected = math.exp(2 * params.mu + params.sigma**2) * (math.exp(params.sigma**2) - 1) * (params.speaker_effect**2)
    assert abs(variance - expected) < 1e-10


def test_expected_duration_for_syllables():
    """Test expected duration for multiple syllables."""
    params = DurationParams()
    
    # Test with 1 syllable
    duration_1 = expected_duration_for_syllables(1, params)
    assert duration_1 > 0
    
    # Test with 10 syllables
    duration_10 = expected_duration_for_syllables(10, params)
    assert duration_10 > duration_1
    assert duration_10 == 10 * duration_1  # Should scale linearly without fatigue


def test_variance_duration_for_syllables():
    """Test variance of duration for multiple syllables."""
    params = DurationParams()
    
    # Test with 1 syllable
    variance_1 = variance_duration_for_syllables(1, params)
    assert variance_1 > 0
    
    # Test with 10 syllables
    variance_10 = variance_duration_for_syllables(10, params)
    assert variance_10 > variance_1
    assert variance_10 == 10 * variance_1  # Should scale linearly


def test_fatigue_effect():
    """Test fatigue effect on duration."""
    params_no_fatigue = DurationParams(fatigue_coeff=0.0)
    params_with_fatigue = DurationParams(fatigue_coeff=0.01)
    
    duration_no_fatigue = expected_duration_for_syllables(100, params_no_fatigue)
    duration_with_fatigue = expected_duration_for_syllables(100, params_with_fatigue)
    
    # With fatigue, duration should be longer
    assert duration_with_fatigue > duration_no_fatigue


def test_speaker_effect():
    """Test speaker effect on duration."""
    params_normal = DurationParams(speaker_effect=1.0)
    params_slow = DurationParams(speaker_effect=1.5)
    
    duration_normal = expected_syllable_duration(params_normal)
    duration_slow = expected_syllable_duration(params_slow)
    
    # Slow speaker should have longer duration
    assert duration_slow > duration_normal
    assert duration_slow == 1.5 * duration_normal


def test_get_default_params():
    """Test getting default parameters."""
    params = get_default_params()
    assert isinstance(params, DurationParams)
    assert params.mu == 0.15
    assert params.sigma == 0.3


def test_create_params():
    """Test creating parameters with custom values."""
    params = create_params(
        mu=0.2,
        sigma=0.4,
        speaker_effect=1.2,
        fatigue_coeff=0.01
    )
    
    assert params.mu == 0.2
    assert params.sigma == 0.4
    assert params.speaker_effect == 1.2
    assert params.fatigue_coeff == 0.01


def test_create_params_partial():
    """Test creating parameters with partial values."""
    params = create_params(mu=0.2)
    
    assert params.mu == 0.2
    assert params.sigma == 0.3  # Default value
    assert params.speaker_effect == 1.0  # Default value


def test_duration_consistency():
    """Test consistency of duration calculations."""
    params = DurationParams()
    
    # Test that the same parameters always give the same results
    duration1 = expected_syllable_duration(params)
    duration2 = expected_syllable_duration(params)
    assert duration1 == duration2
    
    variance1 = variance_syllable_duration(params)
    variance2 = variance_syllable_duration(params)
    assert variance1 == variance2


def test_duration_scaling():
    """Test that duration scales properly with number of syllables."""
    params = DurationParams()
    
    # Test scaling from 1 to 10 syllables
    duration_1 = expected_duration_for_syllables(1, params)
    duration_10 = expected_duration_for_syllables(10, params)
    
    # Should scale linearly without fatigue
    assert abs(duration_10 - 10 * duration_1) < 1e-10
