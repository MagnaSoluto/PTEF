"""
Pauses module for prosodic pause estimation.

Calculates pause counts and durations based on structural and
prosodic boundaries in numerical sequences.
"""

from typing import Dict, Optional
from pydantic import BaseModel


class PauseParams(BaseModel):
    """Parameters for pause estimation."""
    # Pause durations (seconds)
    weak_pause_duration: float = 0.1  # Weak prosodic boundary
    strong_pause_duration: float = 0.3  # Strong prosodic boundary
    
    # Pause probabilities
    weak_pause_prob: float = 0.3  # Probability of weak pause
    strong_pause_prob: float = 0.1  # Probability of strong pause
    
    # Structural pause parameters
    structural_pause_duration: float = 0.2  # Structural pause duration
    structural_pause_prob: float = 0.5  # Probability of structural pause


def count_pauses(
    token_counts: Dict[str, int], 
    B: int = 16, 
    structural: bool = True,
    params: Optional[PauseParams] = None
) -> Dict[str, int]:
    """
    Count pauses based on token counts and block size.
    
    Args:
        token_counts: Dictionary of token counts
        B: Block size for structural pauses
        structural: Whether to include structural pauses
        params: Pause parameters
        
    Returns:
        Dictionary mapping pause types to counts
    """
    if params is None:
        params = PauseParams()
    
    pause_counts = {
        "weak_pauses": 0,
        "strong_pauses": 0,
        "structural_pauses": 0
    }
    
    # Count weak pauses (after connectives)
    if "e" in token_counts:
        pause_counts["weak_pauses"] = int(token_counts["e"] * params.weak_pause_prob)
    
    # Count strong pauses (after major boundaries)
    # Strong boundaries occur after "mil", "milhão", "milhões"
    strong_boundary_tokens = ["mil", "milhão", "milhões"]
    for token in strong_boundary_tokens:
        if token in token_counts:
            pause_counts["strong_pauses"] += int(token_counts[token] * params.strong_pause_prob)
    
    # Count structural pauses (based on block size B)
    if structural:
        total_tokens = sum(token_counts.values())
        num_blocks = (total_tokens + B - 1) // B  # Ceiling division
        pause_counts["structural_pauses"] = int((num_blocks - 1) * params.structural_pause_prob)
    
    return pause_counts


def expected_pause_duration(
    pause_counts: Dict[str, int],
    params: Optional[PauseParams] = None
) -> float:
    """
    Calculate expected total pause duration.
    
    Args:
        pause_counts: Dictionary of pause counts
        params: Pause parameters
        
    Returns:
        Expected total pause duration in seconds
    """
    if params is None:
        params = PauseParams()
    
    total_duration = 0.0
    
    # Add weak pause duration
    total_duration += pause_counts.get("weak_pauses", 0) * params.weak_pause_duration
    
    # Add strong pause duration
    total_duration += pause_counts.get("strong_pauses", 0) * params.strong_pause_duration
    
    # Add structural pause duration
    total_duration += pause_counts.get("structural_pauses", 0) * params.structural_pause_duration
    
    return total_duration


def variance_pause_duration(
    pause_counts: Dict[str, int],
    params: Optional[PauseParams] = None
) -> float:
    """
    Calculate variance of total pause duration.
    
    Args:
        pause_counts: Dictionary of pause counts
        params: Pause parameters
        
    Returns:
        Variance of total pause duration in seconds^2
    """
    if params is None:
        params = PauseParams()
    
    # Assume pause durations are independent and normally distributed
    # with variance equal to mean (exponential-like distribution)
    variance = 0.0
    
    # Add weak pause variance
    weak_count = pause_counts.get("weak_pauses", 0)
    if weak_count > 0:
        variance += weak_count * (params.weak_pause_duration ** 2)
    
    # Add strong pause variance
    strong_count = pause_counts.get("strong_pauses", 0)
    if strong_count > 0:
        variance += strong_count * (params.strong_pause_duration ** 2)
    
    # Add structural pause variance
    structural_count = pause_counts.get("structural_pauses", 0)
    if structural_count > 0:
        variance += structural_count * (params.structural_pause_duration ** 2)
    
    return variance


def get_default_pause_params() -> PauseParams:
    """
    Get default pause parameters.
    
    Returns:
        Default pause parameters
    """
    return PauseParams()


def create_pause_params(
    weak_pause_duration: Optional[float] = None,
    strong_pause_duration: Optional[float] = None,
    weak_pause_prob: Optional[float] = None,
    strong_pause_prob: Optional[float] = None,
    structural_pause_duration: Optional[float] = None,
    structural_pause_prob: Optional[float] = None,
    **kwargs
) -> PauseParams:
    """
    Create pause parameters with specified values.
    
    Args:
        weak_pause_duration: Duration of weak pauses
        strong_pause_duration: Duration of strong pauses
        weak_pause_prob: Probability of weak pauses
        strong_pause_prob: Probability of strong pauses
        structural_pause_duration: Duration of structural pauses
        structural_pause_prob: Probability of structural pauses
        **kwargs: Additional parameters
        
    Returns:
        Pause parameters object
    """
    params = get_default_pause_params()
    
    if weak_pause_duration is not None:
        params.weak_pause_duration = weak_pause_duration
    if strong_pause_duration is not None:
        params.strong_pause_duration = strong_pause_duration
    if weak_pause_prob is not None:
        params.weak_pause_prob = weak_pause_prob
    if strong_pause_prob is not None:
        params.strong_pause_prob = strong_pause_prob
    if structural_pause_duration is not None:
        params.structural_pause_duration = structural_pause_duration
    if structural_pause_prob is not None:
        params.structural_pause_prob = structural_pause_prob
    
    # Update any additional parameters
    for key, value in kwargs.items():
        if hasattr(params, key):
            setattr(params, key, value)
    
    return params
