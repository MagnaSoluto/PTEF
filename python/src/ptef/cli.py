"""
Command-line interface for PTEF.

Provides CLI commands for pronunciation time estimation.
"""

import json
import click
from typing import Optional

from .ptef import estimate, get_default_params, create_params
from .duration import DurationParams
from .pauses import PauseParams


@click.group()
def cli():
    """PTEF - Pronunciation-Time Estimation Framework for Brazilian Portuguese."""
    pass


@cli.command()
@click.option('--N', 'n', required=True, type=int, help='Maximum number to estimate for')
@click.option('--policy', default='R1', help='Grammar policy (currently only R1 supported)')
@click.option('--B', 'b', default=16, type=int, help='Block size for structural pauses')
@click.option('--mu', type=float, help='Mean of log duration')
@click.option('--sigma', type=float, help='Standard deviation of log duration')
@click.option('--speaker-effect', type=float, help='Speaker effect multiplier')
@click.option('--fatigue-coeff', type=float, help='Fatigue coefficient')
@click.option('--weak-pause-duration', type=float, help='Weak pause duration (seconds)')
@click.option('--strong-pause-duration', type=float, help='Strong pause duration (seconds)')
@click.option('--weak-pause-prob', type=float, help='Weak pause probability')
@click.option('--strong-pause-prob', type=float, help='Strong pause probability')
@click.option('--structural-pause-duration', type=float, help='Structural pause duration (seconds)')
@click.option('--structural-pause-prob', type=float, help='Structural pause probability')
@click.option('--no-structural-pauses', is_flag=True, help='Disable structural pauses')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
@click.option('--ci/--no-ci', default=True, help='Include confidence intervals')
def estimate_cmd(
    n: int,
    policy: str,
    b: int,
    mu: Optional[float],
    sigma: Optional[float],
    speaker_effect: Optional[float],
    fatigue_coeff: Optional[float],
    weak_pause_duration: Optional[float],
    strong_pause_duration: Optional[float],
    weak_pause_prob: Optional[float],
    strong_pause_prob: Optional[float],
    structural_pause_duration: Optional[float],
    structural_pause_prob: Optional[float],
    no_structural_pauses: bool,
    output_json: bool,
    ci: bool
):
    """Estimate pronunciation time for numbers 1 to N."""
    
    # Create parameters
    duration_params = None
    if any([mu is not None, sigma is not None, speaker_effect is not None, fatigue_coeff is not None]):
        duration_params = DurationParams(
            mu=mu or 0.15,
            sigma=sigma or 0.3,
            speaker_effect=speaker_effect or 1.0,
            fatigue_coeff=fatigue_coeff or 0.0
        )
    
    pause_params = None
    if any([
        weak_pause_duration is not None, strong_pause_duration is not None,
        weak_pause_prob is not None, strong_pause_prob is not None,
        structural_pause_duration is not None, structural_pause_prob is not None
    ]):
        pause_params = PauseParams(
            weak_pause_duration=weak_pause_duration or 0.1,
            strong_pause_duration=strong_pause_duration or 0.3,
            weak_pause_prob=weak_pause_prob or 0.3,
            strong_pause_prob=strong_pause_prob or 0.1,
            structural_pause_duration=structural_pause_duration or 0.2,
            structural_pause_prob=structural_pause_prob or 0.5
        )
    
    params = create_params(
        duration_params=duration_params,
        pause_params=pause_params,
        block_size=b,
        include_structural_pauses=not no_structural_pauses
    )
    
    # Run estimation
    try:
        result = estimate(n, policy, b, params, return_ci=ci)
        
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            # Human-readable output
            click.echo(f"PTEF Estimation Results for N={n}")
            click.echo(f"Policy: {policy}, Block size: {b}")
            click.echo(f"Expected duration: {result['mean']:.3f} seconds")
            click.echo(f"Variance: {result['var']:.6f} seconds²")
            
            if ci and 'ci95' in result:
                ci95 = result['ci95']
                click.echo(f"95% Confidence Interval: [{ci95['lower']:.3f}, {ci95['upper']:.3f}] seconds")
            
            # Show details
            details = result['details']
            click.echo(f"\nDetails:")
            click.echo(f"  Total syllables: {details['total_syllables']}")
            click.echo(f"  Syllable duration: {details['syllable_duration']:.3f} seconds")
            click.echo(f"  Pause duration: {details['pause_duration']:.3f} seconds")
            click.echo(f"  Pause counts: {details['pause_counts']}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--N', 'n', required=True, type=int, help='Maximum number to estimate for')
@click.option('--policy', default='R1', help='Grammar policy')
@click.option('--B', 'b', default=16, type=int, help='Block size for structural pauses')
@click.option('--json', 'output_json', is_flag=True, help='Output in JSON format')
def validate(n: int, policy: str, b: int, output_json: bool):
    """Validate PTEF implementation against direct counting."""
    from .combinatorics import count_tokens_up_to_N
    from .grammar import text_number
    
    # Direct counting
    direct_counts = {}
    for i in range(1, n + 1):
        tokens = text_number(i)
        for token in tokens:
            direct_counts[token] = direct_counts.get(token, 0) + 1
    
    # Fast counting
    fast_counts, _ = count_tokens_up_to_N(n, policy)
    
    # Compare
    all_tokens = set(direct_counts.keys()) | set(fast_counts.keys())
    differences = {}
    
    for token in all_tokens:
        direct_count = direct_counts.get(token, 0)
        fast_count = fast_counts.get(token, 0)
        if direct_count != fast_count:
            differences[token] = {
                'direct': direct_count,
                'fast': fast_count,
                'diff': fast_count - direct_count
            }
    
    if output_json:
        result = {
            'n': n,
            'policy': policy,
            'block_size': b,
            'validation_passed': len(differences) == 0,
            'differences': differences,
            'total_tokens_direct': sum(direct_counts.values()),
            'total_tokens_fast': sum(fast_counts.values())
        }
        click.echo(json.dumps(result, indent=2))
    else:
        if differences:
            click.echo(f"Validation FAILED for N={n}")
            click.echo("Differences found:")
            for token, diff in differences.items():
                click.echo(f"  {token}: direct={diff['direct']}, fast={diff['fast']}, diff={diff['diff']}")
        else:
            click.echo(f"Validation PASSED for N={n}")
            click.echo(f"Total tokens: {sum(direct_counts.values())}")


@cli.command()
def info():
    """Show PTEF information and version."""
    from . import __version__, __author__, __email__
    
    click.echo(f"PTEF - Pronunciation-Time Estimation Framework")
    click.echo(f"Version: {__version__}")
    click.echo(f"Author: {__author__}")
    click.echo(f"Email: {__email__}")
    click.echo(f"Description: A probabilistic framework for estimating pronunciation time")
    click.echo(f"of numerical sequences in Brazilian Portuguese.")


if __name__ == '__main__':
    cli()
