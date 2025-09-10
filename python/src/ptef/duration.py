"""
Duration module for syllable duration estimation.

Implements lognormal microduration models for syllable timing
in Brazilian Portuguese.
"""

import math
from typing import Dict, Optional
from pydantic import BaseModel


class DurationParams(BaseModel):
    """Parameters for duration estimation."""
    # Lognormal parameters for syllable duration
    mu: float = 0.15  # Mean of log duration (seconds)
    sigma: float = 0.3  # Standard deviation of log duration
    
    # Speaker effects
    speaker_effect: float = 1.0  # Multiplicative speaker effect
    
    # Fatigue coefficient
    fatigue_coeff: float = 0.0  # Linear fatigue effect per syllable
    
    # Syllable type effects
    vowel_duration_mult: float = 1.0  # Vowel duration multiplier
    consonant_duration_mult: float = 1.0  # Consonant duration multiplier
    
    # Stress effects
    stressed_mult: float = 1.2  # Stressed syllable multiplier
    unstressed_mult: float = 0.9  # Unstressed syllable multiplier


def expected_syllable_duration(params: Optional[DurationParams] = None) -> float:
    """
    Calculate expected syllable duration using lognormal model.
    
    Args:
        params: Duration parameters (uses defaults if None)
        
    Returns:
        Expected syllable duration in seconds
    """
    if params is None:
        params = DurationParams()
    
    # Lognormal mean: exp(mu + sigma^2/2)
    lognormal_mean = math.exp(params.mu + (params.sigma**2) / 2)
    
    # Apply speaker effect
    return lognormal_mean * params.speaker_effect


def variance_syllable_duration(params: Optional[DurationParams] = None) -> float:
    """
    Calculate variance of syllable duration using lognormal model.
    
    Args:
        params: Duration parameters (uses defaults if None)
        
    Returns:
        Variance of syllable duration in seconds^2
    """
    if params is None:
        params = DurationParams()
    
    # Lognormal variance: exp(2*mu + sigma^2) * (exp(sigma^2) - 1)
    variance = math.exp(2 * params.mu + params.sigma**2) * (math.exp(params.sigma**2) - 1)
    
    # Apply speaker effect squared
    return variance * (params.speaker_effect**2)


def expected_duration_for_syllables(num_syllables: int, params: Optional[DurationParams] = None) -> float:
    """
    Calculate expected duration for a given number of syllables.
    
    Args:
        num_syllables: Number of syllables
        params: Duration parameters
        
    Returns:
        Expected total duration in seconds
    """
    if params is None:
        params = DurationParams()
    
    base_duration = expected_syllable_duration(params)
    
    # Apply fatigue effect
    fatigue_effect = 1.0 + params.fatigue_coeff * num_syllables
    
    return base_duration * num_syllables * fatigue_effect


def variance_duration_for_syllables(num_syllables: int, params: Optional[DurationParams] = None) -> float:
    """
    Calculate variance of duration for a given number of syllables.
    
    Args:
        num_syllables: Number of syllables
        params: Duration parameters
        
    Returns:
        Variance of total duration in seconds^2
    """
    if params is None:
        params = DurationParams()
    
    base_variance = variance_syllable_duration(params)
    
    # For independent syllables, variance scales linearly
    return base_variance * num_syllables


def get_default_params() -> DurationParams:
    """
    Get default duration parameters.
    
    Returns:
        Default duration parameters
    """
    return DurationParams()


def create_params(
    mu: Optional[float] = None,
    sigma: Optional[float] = None,
    speaker_effect: Optional[float] = None,
    fatigue_coeff: Optional[float] = None,
    **kwargs
) -> DurationParams:
    """
    Create duration parameters with specified values.
    
    Args:
        mu: Mean of log duration
        sigma: Standard deviation of log duration
        speaker_effect: Speaker effect multiplier
        fatigue_coeff: Fatigue coefficient
        **kwargs: Additional parameters
        
    Returns:
        Duration parameters object
    """
    params = get_default_params()
    
    if mu is not None:
        params.mu = mu
    if sigma is not None:
        params.sigma = sigma
    if speaker_effect is not None:
        params.speaker_effect = speaker_effect
    if fatigue_coeff is not None:
        params.fatigue_coeff = fatigue_coeff
    
    # Update any additional parameters
    for key, value in kwargs.items():
        if hasattr(params, key):
            setattr(params, key, value)
    
    return params
