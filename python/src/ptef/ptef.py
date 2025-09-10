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
from .context import ContextModel, extract_context_features, expected_duration_with_context, variance_duration_with_context
from .bootstrap import bootstrap_estimate, BootstrapConfig


class PTEFParams(BaseModel):
    """Parameters for PTEF estimation."""
    # Duration parameters
    duration_params: Optional[DurationParams] = None
    
    # Pause parameters
    pause_params: Optional[PauseParams] = None
    
    # Context parameters
    context_model: Optional[ContextModel] = None
    
    # Bootstrap parameters
    bootstrap_config: Optional[BootstrapConfig] = None
    
    # Block size for structural pauses
    block_size: int = 16
    
    # Whether to include structural pauses
    include_structural_pauses: bool = True
    
    # Whether to use context-aware duration
    use_context: bool = False
    
    # Whether to use bootstrap for CI
    use_bootstrap: bool = False


def estimate(
    N: int,
    policy: str = "R1",
    B: int = 16,
    params: Optional[PTEFParams] = None,
    return_ci: bool = True,
    use_bootstrap: bool = False
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
    
    # Use bootstrap if requested
    if use_bootstrap or (params.use_bootstrap and params.bootstrap_config is not None):
        return _estimate_with_bootstrap(N, policy, B, params, return_ci)
    
    # Get token counts
    token_counts, connective_counts = count_tokens_up_to_N(N, policy)
    
    # Count syllables
    total_syllables = count_syllables_up_to_N(N, policy)
    
    # Calculate syllable duration
    if params.use_context and params.context_model is not None:
        # Use context-aware duration calculation
        syllable_duration, syllable_variance = _calculate_context_duration(
            token_counts, params.context_model
        )
    else:
        # Use standard duration calculation
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


def _estimate_with_bootstrap(
    N: int,
    policy: str,
    B: int,
    params: PTEFParams,
    return_ci: bool
) -> Dict:
    """
    Estimate using bootstrap method.
    
    Args:
        N: Maximum number to estimate for
        policy: Grammar policy
        B: Block size for structural pauses
        params: PTEF parameters
        return_ci: Whether to return confidence intervals
        
    Returns:
        Dictionary with bootstrap results
    """
    # Use bootstrap estimation
    bootstrap_result = bootstrap_estimate(
        N, policy, B, params.bootstrap_config, 
        params.context_model.model_dump() if params.context_model else None
    )
    
    # Prepare details
    token_counts, connective_counts = count_tokens_up_to_N(N, policy)
    pause_counts = count_pauses(token_counts, B, params.include_structural_pauses, params.pause_params)
    
    details = {
        "total_syllables": count_syllables_up_to_N(N, policy),
        "syllable_duration": bootstrap_result["mean"] * 0.8,  # Approximate split
        "syllable_variance": bootstrap_result["var"] * 0.8,
        "pause_counts": pause_counts,
        "pause_duration": bootstrap_result["mean"] * 0.2,  # Approximate split
        "pause_variance": bootstrap_result["var"] * 0.2,
        "token_counts": token_counts,
        "connective_counts": connective_counts,
        "bootstrap_samples": bootstrap_result.get("samples", [])
    }
    
    result = {
        "mean": bootstrap_result["mean"],
        "var": bootstrap_result["var"],
        "details": details
    }
    
    if return_ci and "bootstrap_ci" in bootstrap_result:
        result["ci95"] = {
            "lower": bootstrap_result["bootstrap_ci"]["lower"],
            "upper": bootstrap_result["bootstrap_ci"]["upper"],
            "method": bootstrap_result["bootstrap_ci"]["method"]
        }
    
    return result


def _calculate_context_duration(
    token_counts: Dict[str, int],
    context_model: ContextModel
) -> Tuple[float, float]:
    """
    Calculate duration using context-aware model.
    
    Args:
        token_counts: Token counts
        context_model: Context model
        
    Returns:
        Tuple of (duration, variance)
    """
    total_duration = 0.0
    total_variance = 0.0
    
    # Simulate context for each token type
    recent_tokens = []
    accumulated_syllables = 0
    
    for token, count in token_counts.items():
        if token == "e":  # Skip connectives for syllable counting
            continue
        
        try:
            from .lexicon import syllables
            s_t = syllables(token)
            
            # Extract context features
            features = extract_context_features(
                token, 0, recent_tokens, accumulated_syllables
            )
            
            # Calculate context-aware duration
            duration = expected_duration_with_context(token, features, context_model)
            variance = variance_duration_with_context(token, features, context_model)
            
            # Add to totals
            total_duration += duration * count
            total_variance += variance * count
            
            # Update context
            recent_tokens.append(token)
            accumulated_syllables += s_t * count
            
            # Keep recent tokens list manageable
            if len(recent_tokens) > 10:
                recent_tokens = recent_tokens[-10:]
                
        except KeyError:
            # Skip unknown tokens
            continue
    
    return total_duration, total_variance
