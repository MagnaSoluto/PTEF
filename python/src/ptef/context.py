"""
Context module for conditional duration modeling.

Implements context-aware duration estimation as described in the paper,
where syllable duration depends on contextual features.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel


class ContextFeatures(BaseModel):
    """Contextual features for duration modeling."""
    position_in_group: int  # Position within current group (0-999)
    recent_complexity: float  # Average syllables of recent tokens
    has_long_words: bool  # Whether recent tokens are long
    speaker_effect: float  # Speaker-specific multiplier
    fatigue: float  # Accumulated fatigue effect
    is_connective: bool  # Whether token is a connective ("e")
    is_boundary: bool  # Whether token is at prosodic boundary
    stress_pattern: str  # Stress pattern (stressed/unstressed)


class ContextModel(BaseModel):
    """Context model parameters."""
    # Beta coefficients for context features
    beta_position: float = 0.001
    beta_complexity: float = 0.05
    beta_long_words: float = 0.02
    beta_connective: float = -0.1
    beta_boundary: float = 0.15
    beta_stress: float = 0.1
    
    # Base parameters
    mu_base: float = 0.15
    sigma: float = 0.3
    
    # Fatigue parameters
    fatigue_coeff: float = 0.0001
    fatigue_threshold: int = 1000
    
    # Speaker effects
    speaker_effects: Dict[str, float] = {"default": 1.0}


def extract_context_features(
    token: str,
    position: int,
    recent_tokens: List[str],
    accumulated_syllables: int,
    speaker_id: str = "default",
    is_boundary: bool = False
) -> ContextFeatures:
    """
    Extract contextual features for a token.
    
    Args:
        token: Current token
        position: Position in current group (0-999)
        recent_tokens: Recent tokens for context
        accumulated_syllables: Total syllables processed so far
        speaker_id: Speaker identifier
        is_boundary: Whether at prosodic boundary
        
    Returns:
        Context features object
    """
    # Calculate recent complexity (average syllables of last 5 tokens)
    recent_syllables = []
    for t in recent_tokens[-5:]:
        try:
            from .lexicon import syllables
            recent_syllables.append(syllables(t))
        except KeyError:
            recent_syllables.append(1)  # Default for unknown tokens
    
    recent_complexity = np.mean(recent_syllables) if recent_syllables else 1.0
    
    # Check for long words (tokens with > 8 characters)
    has_long_words = any(len(t) > 8 for t in recent_tokens[-3:])
    
    # Calculate fatigue effect
    fatigue = min(accumulated_syllables * 0.0001, 0.5)  # Cap at 50% increase
    
    # Determine stress pattern (simplified)
    stress_pattern = "stressed" if position % 10 == 0 else "unstressed"
    
    return ContextFeatures(
        position_in_group=position,
        recent_complexity=recent_complexity,
        has_long_words=has_long_words,
        speaker_effect=1.0,  # Will be overridden by model
        fatigue=fatigue,
        is_connective=(token == "e"),
        is_boundary=is_boundary,
        stress_pattern=stress_pattern
    )


def compute_contextual_mu(
    features: ContextFeatures,
    model: ContextModel
) -> float:
    """
    Compute contextual mean μ(x) = βᵀx as in the paper.
    
    Args:
        features: Context features
        model: Context model parameters
        
    Returns:
        Contextual mean μ(x)
    """
    # Build feature vector x
    x = np.array([
        features.position_in_group / 1000.0,  # Normalized position
        features.recent_complexity,
        float(features.has_long_words),
        float(features.is_connective),
        float(features.is_boundary),
        1.0 if features.stress_pattern == "stressed" else 0.0
    ])
    
    # Beta coefficients
    beta = np.array([
        model.beta_position,
        model.beta_complexity,
        model.beta_long_words,
        model.beta_connective,
        model.beta_boundary,
        model.beta_stress
    ])
    
    # Compute μ(x) = βᵀx + μ_base
    mu = np.dot(beta, x) + model.mu_base
    
    # Apply speaker effect
    speaker_effect = model.speaker_effects.get("default", 1.0)
    mu += np.log(speaker_effect)  # Additive in log space
    
    # Apply fatigue effect
    mu += features.fatigue
    
    return mu


def expected_duration_with_context(
    token: str,
    features: ContextFeatures,
    model: ContextModel
) -> float:
    """
    Compute expected duration with context: E[d(t)|x] = s(t) · exp(μ(x) + σ²/2)
    
    Args:
        token: Token to compute duration for
        features: Context features
        model: Context model
        
    Returns:
        Expected duration in seconds
    """
    from .lexicon import syllables
    
    # Get syllable count
    s_t = syllables(token)
    
    # Compute contextual mean
    mu_x = compute_contextual_mu(features, model)
    
    # Expected duration: s(t) · exp(μ(x) + σ²/2)
    expected_duration = s_t * np.exp(mu_x + (model.sigma**2) / 2)
    
    return expected_duration


def variance_duration_with_context(
    token: str,
    features: ContextFeatures,
    model: ContextModel
) -> float:
    """
    Compute variance with context: Var[d(t)|x] = s(t)² · exp(2μ(x) + σ²) · (exp(σ²) - 1)
    
    Args:
        token: Token to compute variance for
        features: Context features
        model: Context model
        
    Returns:
        Variance in seconds²
    """
    from .lexicon import syllables
    
    # Get syllable count
    s_t = syllables(token)
    
    # Compute contextual mean
    mu_x = compute_contextual_mu(features, model)
    
    # Variance: s(t)² · exp(2μ(x) + σ²) · (exp(σ²) - 1)
    variance = (s_t**2) * np.exp(2 * mu_x + model.sigma**2) * (np.exp(model.sigma**2) - 1)
    
    return variance


def get_default_context_model() -> ContextModel:
    """
    Get default context model parameters.
    
    Returns:
        Default context model
    """
    return ContextModel()


def create_context_model(
    beta_position: Optional[float] = None,
    beta_complexity: Optional[float] = None,
    beta_long_words: Optional[float] = None,
    beta_connective: Optional[float] = None,
    beta_boundary: Optional[float] = None,
    beta_stress: Optional[float] = None,
    mu_base: Optional[float] = None,
    sigma: Optional[float] = None,
    fatigue_coeff: Optional[float] = None,
    speaker_effects: Optional[Dict[str, float]] = None,
    **kwargs
) -> ContextModel:
    """
    Create context model with specified parameters.
    
    Args:
        beta_position: Position coefficient
        beta_complexity: Complexity coefficient
        beta_long_words: Long words coefficient
        beta_connective: Connective coefficient
        beta_boundary: Boundary coefficient
        beta_stress: Stress coefficient
        mu_base: Base mean
        sigma: Standard deviation
        fatigue_coeff: Fatigue coefficient
        speaker_effects: Speaker effects dictionary
        **kwargs: Additional parameters
        
    Returns:
        Context model object
    """
    model = get_default_context_model()
    
    if beta_position is not None:
        model.beta_position = beta_position
    if beta_complexity is not None:
        model.beta_complexity = beta_complexity
    if beta_long_words is not None:
        model.beta_long_words = beta_long_words
    if beta_connective is not None:
        model.beta_connective = beta_connective
    if beta_boundary is not None:
        model.beta_boundary = beta_boundary
    if beta_stress is not None:
        model.beta_stress = beta_stress
    if mu_base is not None:
        model.mu_base = mu_base
    if sigma is not None:
        model.sigma = sigma
    if fatigue_coeff is not None:
        model.fatigue_coeff = fatigue_coeff
    if speaker_effects is not None:
        model.speaker_effects = speaker_effects
    
    # Update any additional parameters
    for key, value in kwargs.items():
        if hasattr(model, key):
            setattr(model, key, value)
    
    return model
