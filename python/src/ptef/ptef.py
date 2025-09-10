"""
Main PTEF module for pronunciation time estimation.

Orchestrates all components to estimate pronunciation time
for numerical sequences in Brazilian Portuguese.
"""

from typing import Dict, Optional, Tuple
import math
from pydantic import BaseModel

from .combinatorics import count_tokens_up_to_N, count_syllables_up_to_N
from .duration import DurationParams, expected_duration_for_syllables, variance_duration_for_syllables
from .pauses import PauseParams, count_pauses, expected_pause_duration, variance_pause_duration


class PTEFParams(BaseModel):
    """Parameters for PTEF estimation."""
    # Duration parameters
    duration_params: Optional[DurationParams] = None
    
    # Pause parameters
    pause_params: Optional[PauseParams] = None
    
    # Block size for structural pauses
    block_size: int = 16
    
    # Whether to include structural pauses
    include_structural_pauses: bool = True


def estimate(
    N: int,
    policy: str = "R1",
    B: int = 16,
    params: Optional[PTEFParams] = None,
    return_ci: bool = True
) -> Dict:
    """
    Estimate pronunciation time for numbers 1 to N.
    
    Args:
        N: Maximum number to estimate for
        policy: Grammar policy (currently only "R1" supported)
        B: Block size for structural pauses
        params: PTEF parameters (uses defaults if None)
        return_ci: Whether to return confidence intervals
        
    Returns:
        Dictionary containing:
        - mean: Expected pronunciation time (seconds)
        - var: Variance of pronunciation time (seconds^2)
        - ci95: 95% confidence interval (if return_ci=True)
        - details: Detailed breakdown of components
    """
    if params is None:
        params = PTEFParams()
    
    # Get token counts
    token_counts, connective_counts = count_tokens_up_to_N(N, policy)
    
    # Count syllables
    total_syllables = count_syllables_up_to_N(N, policy)
    
    # Calculate syllable duration
    syllable_duration = expected_duration_for_syllables(
        total_syllables, 
        params.duration_params
    )
    syllable_variance = variance_duration_for_syllables(
        total_syllables, 
        params.duration_params
    )
    
    # Calculate pause duration
    pause_counts = count_pauses(
        token_counts, 
        B, 
        params.include_structural_pauses,
        params.pause_params
    )
    
    pause_duration = expected_pause_duration(pause_counts, params.pause_params)
    pause_variance = variance_pause_duration(pause_counts, params.pause_params)
    
    # Total duration and variance
    total_duration = syllable_duration + pause_duration
    total_variance = syllable_variance + pause_variance
    
    # Calculate confidence interval
    ci95 = None
    if return_ci:
        std_dev = math.sqrt(total_variance)
        ci95 = {
            "lower": total_duration - 1.96 * std_dev,
            "upper": total_duration + 1.96 * std_dev
        }
    
    # Prepare details
    details = {
        "total_syllables": total_syllables,
        "syllable_duration": syllable_duration,
        "syllable_variance": syllable_variance,
        "pause_counts": pause_counts,
        "pause_duration": pause_duration,
        "pause_variance": pause_variance,
        "token_counts": token_counts,
        "connective_counts": connective_counts
    }
    
    result = {
        "mean": total_duration,
        "var": total_variance,
        "details": details
    }
    
    if ci95 is not None:
        result["ci95"] = ci95
    
    return result


def get_default_params() -> PTEFParams:
    """
    Get default PTEF parameters.
    
    Returns:
        Default PTEF parameters
    """
    return PTEFParams()


def create_params(
    duration_params: Optional[DurationParams] = None,
    pause_params: Optional[PauseParams] = None,
    block_size: Optional[int] = None,
    include_structural_pauses: Optional[bool] = None,
    **kwargs
) -> PTEFParams:
    """
    Create PTEF parameters with specified values.
    
    Args:
        duration_params: Duration parameters
        pause_params: Pause parameters
        block_size: Block size for structural pauses
        include_structural_pauses: Whether to include structural pauses
        **kwargs: Additional parameters
        
    Returns:
        PTEF parameters object
    """
    params = get_default_params()
    
    if duration_params is not None:
        params.duration_params = duration_params
    if pause_params is not None:
        params.pause_params = pause_params
    if block_size is not None:
        params.block_size = block_size
    if include_structural_pauses is not None:
        params.include_structural_pauses = include_structural_pauses
    
    # Update any additional parameters
    for key, value in kwargs.items():
        if hasattr(params, key):
            setattr(params, key, value)
    
    return params


def estimate_batch(
    N_values: list,
    policy: str = "R1",
    B: int = 16,
    params: Optional[PTEFParams] = None
) -> Dict[int, Dict]:
    """
    Estimate pronunciation time for multiple N values.
    
    Args:
        N_values: List of N values to estimate for
        policy: Grammar policy
        B: Block size for structural pauses
        params: PTEF parameters
        
    Returns:
        Dictionary mapping N values to estimation results
    """
    results = {}
    
    for N in N_values:
        results[N] = estimate(N, policy, B, params, return_ci=True)
    
    return results
