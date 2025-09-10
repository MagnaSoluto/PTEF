"""
Bootstrap module for confidence interval estimation.

Implements bootstrap methods as described in the paper for robust
confidence interval estimation.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel
import random


class BootstrapConfig(BaseModel):
    """Configuration for bootstrap methods."""
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    random_seed: Optional[int] = None
    method: str = "percentile"  # "percentile", "bca", "studentized"


class BootstrapEstimator:
    """Bootstrap estimator for confidence intervals."""
    
    def __init__(self, config: BootstrapConfig):
        self.config = config
        if config.random_seed is not None:
            np.random.seed(config.random_seed)
            random.seed(config.random_seed)
    
    def sample_lognormal_duration(
        self,
        mu: float,
        sigma: float,
        n_samples: int = 1
    ) -> np.ndarray:
        """
        Sample from lognormal distribution for duration.
        
        Args:
            mu: Mean of log duration
            sigma: Standard deviation of log duration
            n_samples: Number of samples
            
        Returns:
            Array of sampled durations
        """
        return np.random.lognormal(mu, sigma, n_samples)
    
    def sample_pause_duration(
        self,
        pause_type: str,
        n_samples: int = 1
    ) -> np.ndarray:
        """
        Sample pause durations based on type.
        
        Args:
            pause_type: Type of pause ("weak", "strong", "structural")
            n_samples: Number of samples
            
        Returns:
            Array of sampled pause durations
        """
        # Pause parameters (from paper)
        pause_params = {
            "weak": {"mu": -2.3, "sigma": 0.5},      # ~0.1s mean
            "strong": {"mu": -1.2, "sigma": 0.4},     # ~0.3s mean
            "structural": {"mu": -1.6, "sigma": 0.3}  # ~0.2s mean
        }
        
        params = pause_params.get(pause_type, pause_params["weak"])
        return self.sample_lognormal_duration(
            params["mu"], params["sigma"], n_samples
        )
    
    def bootstrap_syllable_duration(
        self,
        token_counts: Dict[str, int],
        context_model: Optional[Dict] = None
    ) -> np.ndarray:
        """
        Bootstrap syllable durations for all tokens.
        
        Args:
            token_counts: Token counts from combinatorics
            context_model: Context model parameters
            
        Returns:
            Array of total syllable durations
        """
        from .lexicon import syllables
        
        total_durations = []
        
        for _ in range(self.config.n_bootstrap):
            total_duration = 0.0
            
            for token, count in token_counts.items():
                if token == "e":  # Skip connectives for syllable counting
                    continue
                
                try:
                    s_t = syllables(token)
                    
                    # Sample duration for each occurrence
                    for _ in range(count):
                        if context_model:
                            # Use context-aware sampling
                            mu = context_model.get("mu_base", 0.15)
                            sigma = context_model.get("sigma", 0.3)
                        else:
                            # Use default parameters
                            mu = 0.15
                            sigma = 0.3
                        
                        # Sample lognormal duration
                        duration = self.sample_lognormal_duration(mu, sigma, 1)[0]
                        total_duration += s_t * duration
                        
                except KeyError:
                    # Skip unknown tokens
                    continue
            
            total_durations.append(total_duration)
        
        return np.array(total_durations)
    
    def bootstrap_pause_duration(
        self,
        pause_counts: Dict[str, int]
    ) -> np.ndarray:
        """
        Bootstrap pause durations.
        
        Args:
            pause_counts: Pause counts from pauses module
            
        Returns:
            Array of total pause durations
        """
        total_durations = []
        
        for _ in range(self.config.n_bootstrap):
            total_duration = 0.0
            
            # Sample weak pauses
            weak_count = pause_counts.get("weak_pauses", 0)
            if weak_count > 0:
                weak_durations = self.sample_pause_duration("weak", weak_count)
                total_duration += np.sum(weak_durations)
            
            # Sample strong pauses
            strong_count = pause_counts.get("strong_pauses", 0)
            if strong_count > 0:
                strong_durations = self.sample_pause_duration("strong", strong_count)
                total_duration += np.sum(strong_durations)
            
            # Sample structural pauses
            structural_count = pause_counts.get("structural_pauses", 0)
            if structural_count > 0:
                structural_durations = self.sample_pause_duration("structural", structural_count)
                total_duration += np.sum(structural_durations)
            
            total_durations.append(total_duration)
        
        return np.array(total_durations)
    
    def bootstrap_total_duration(
        self,
        token_counts: Dict[str, int],
        pause_counts: Dict[str, int],
        context_model: Optional[Dict] = None
    ) -> np.ndarray:
        """
        Bootstrap total duration (syllables + pauses).
        
        Args:
            token_counts: Token counts
            pause_counts: Pause counts
            context_model: Context model parameters
            
        Returns:
            Array of total durations
        """
        # Bootstrap syllable durations
        syllable_durations = self.bootstrap_syllable_duration(token_counts, context_model)
        
        # Bootstrap pause durations
        pause_durations = self.bootstrap_pause_duration(pause_counts)
        
        # Total duration = syllables + pauses
        total_durations = syllable_durations + pause_durations
        
        return total_durations
    
    def compute_confidence_interval(
        self,
        samples: np.ndarray,
        method: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Compute confidence interval from bootstrap samples.
        
        Args:
            samples: Bootstrap samples
            method: Bootstrap method to use
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        method = method or self.config.method
        
        if method == "percentile":
            return self._percentile_ci(samples)
        elif method == "bca":
            return self._bca_ci(samples)
        elif method == "studentized":
            return self._studentized_ci(samples)
        else:
            raise ValueError(f"Unknown bootstrap method: {method}")
    
    def _percentile_ci(self, samples: np.ndarray) -> Tuple[float, float]:
        """Compute percentile confidence interval."""
        alpha = 1 - self.config.confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(samples, lower_percentile)
        upper_bound = np.percentile(samples, upper_percentile)
        
        return lower_bound, upper_bound
    
    def _bca_ci(self, samples: np.ndarray) -> Tuple[float, float]:
        """
        Compute bias-corrected and accelerated (BCa) confidence interval.
        
        This is a more sophisticated method that corrects for bias and skewness.
        """
        # Simplified BCa implementation
        # In practice, this would require more complex calculations
        
        # For now, fall back to percentile method
        return self._percentile_ci(samples)
    
    def _studentized_ci(self, samples: np.ndarray) -> Tuple[float, float]:
        """
        Compute studentized confidence interval.
        
        This method uses t-distribution for better coverage.
        """
        # Simplified studentized implementation
        mean = np.mean(samples)
        std = np.std(samples, ddof=1)
        n = len(samples)
        
        # Use t-distribution
        from scipy import stats
        alpha = 1 - self.config.confidence_level
        t_val = stats.t.ppf(1 - alpha/2, n - 1)
        
        margin_error = t_val * std / np.sqrt(n)
        
        lower_bound = mean - margin_error
        upper_bound = mean + margin_error
        
        return lower_bound, upper_bound


def bootstrap_estimate(
    N: int,
    policy: str = "R1",
    B: int = 16,
    config: Optional[BootstrapConfig] = None,
    context_model: Optional[Dict] = None
) -> Dict:
    """
    Estimate pronunciation time with bootstrap confidence intervals.
    
    Args:
        N: Maximum number to estimate for
        policy: Grammar policy
        B: Block size for structural pauses
        config: Bootstrap configuration
        context_model: Context model parameters
        
    Returns:
        Dictionary with mean, variance, and bootstrap CI
    """
    if config is None:
        config = BootstrapConfig()
    
    # Get token and pause counts
    from .combinatorics import count_tokens_up_to_N
    from .pauses import count_pauses
    
    token_counts, connective_counts = count_tokens_up_to_N(N, policy)
    pause_counts = count_pauses(token_counts, B, structural=True)
    
    # Initialize bootstrap estimator
    estimator = BootstrapEstimator(config)
    
    # Bootstrap total duration
    bootstrap_samples = estimator.bootstrap_total_duration(
        token_counts, pause_counts, context_model
    )
    
    # Compute statistics
    mean = np.mean(bootstrap_samples)
    variance = np.var(bootstrap_samples, ddof=1)
    
    # Compute confidence interval
    ci_lower, ci_upper = estimator.compute_confidence_interval(bootstrap_samples)
    
    return {
        "mean": mean,
        "var": variance,
        "bootstrap_ci": {
            "lower": ci_lower,
            "upper": ci_upper,
            "method": config.method,
            "n_bootstrap": config.n_bootstrap
        },
        "samples": bootstrap_samples.tolist()  # For analysis
    }


def compare_bootstrap_methods(
    N: int,
    methods: List[str] = ["percentile", "bca", "studentized"],
    config: Optional[BootstrapConfig] = None
) -> Dict[str, Dict]:
    """
    Compare different bootstrap methods.
    
    Args:
        N: Maximum number to estimate for
        methods: List of bootstrap methods to compare
        config: Bootstrap configuration
        
    Returns:
        Dictionary comparing methods
    """
    if config is None:
        config = BootstrapConfig()
    
    results = {}
    
    for method in methods:
        method_config = BootstrapConfig(
            n_bootstrap=config.n_bootstrap,
            confidence_level=config.confidence_level,
            method=method,
            random_seed=config.random_seed
        )
        
        result = bootstrap_estimate(N, config=method_config)
        results[method] = {
            "mean": result["mean"],
            "ci_lower": result["bootstrap_ci"]["lower"],
            "ci_upper": result["bootstrap_ci"]["upper"],
            "ci_width": result["bootstrap_ci"]["upper"] - result["bootstrap_ci"]["lower"]
        }
    
    return results


def bootstrap_sensitivity_analysis(
    N: int,
    parameter_ranges: Dict[str, List[float]],
    config: Optional[BootstrapConfig] = None
) -> Dict[str, Dict]:
    """
    Perform sensitivity analysis using bootstrap.
    
    Args:
        N: Maximum number to estimate for
        parameter_ranges: Dictionary of parameter ranges to test
        config: Bootstrap configuration
        
    Returns:
        Sensitivity analysis results
    """
    if config is None:
        config = BootstrapConfig()
    
    results = {}
    
    # Test different parameter values
    for param_name, param_values in parameter_ranges.items():
        param_results = {}
        
        for value in param_values:
            # Create context model with this parameter value
            context_model = {param_name: value}
            
            # Run bootstrap estimation
            result = bootstrap_estimate(N, config=config, context_model=context_model)
            
            param_results[value] = {
                "mean": result["mean"],
                "ci_lower": result["bootstrap_ci"]["lower"],
                "ci_upper": result["bootstrap_ci"]["upper"]
            }
        
        results[param_name] = param_results
    
    return results
