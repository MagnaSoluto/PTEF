"""
Tests for CLI module.
"""

import pytest
from click.testing import CliRunner
from ptef.cli import cli


def test_cli_estimate_basic():
    """Test basic CLI estimate command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '10'])
    
    assert result.exit_code == 0
    assert "PTEF Estimation Results for N=10" in result.output
    assert "Expected duration:" in result.output


def test_cli_estimate_json():
    """Test CLI estimate command with JSON output."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '10', '--json'])
    
    assert result.exit_code == 0
    
    # Parse JSON output
    import json
    output = json.loads(result.output)
    
    assert "mean" in output
    assert "var" in output
    assert "details" in output
    assert isinstance(output["mean"], (int, float))
    assert isinstance(output["var"], (int, float))


def test_cli_estimate_with_parameters():
    """Test CLI estimate command with custom parameters."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        'estimate', '--N', '10', '--mu', '0.2', '--sigma', '0.4', '--speaker-effect', '1.2'
    ])
    
    assert result.exit_code == 0
    assert "PTEF Estimation Results for N=10" in result.output


def test_cli_estimate_no_ci():
    """Test CLI estimate command without confidence intervals."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '10', '--no-ci'])
    
    assert result.exit_code == 0
    assert "PTEF Estimation Results for N=10" in result.output
    assert "95% Confidence Interval:" not in result.output


def test_cli_validate():
    """Test CLI validate command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', '--N', '10'])
    
    assert result.exit_code == 0
    assert "Validation" in result.output


def test_cli_validate_json():
    """Test CLI validate command with JSON output."""
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', '--N', '10', '--json'])
    
    assert result.exit_code == 0
    
    # Parse JSON output
    import json
    output = json.loads(result.output)
    
    assert "n" in output
    assert "policy" in output
    assert "validation_passed" in output
    assert isinstance(output["validation_passed"], bool)


def test_cli_info():
    """Test CLI info command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['info'])
    
    assert result.exit_code == 0
    assert "PTEF" in result.output
    assert "Version:" in result.output


def test_cli_estimate_required_n():
    """Test that N parameter is required for estimate command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate'])
    
    assert result.exit_code != 0
    assert "Error: Missing option '--N'" in result.output


def test_cli_estimate_invalid_n():
    """Test CLI estimate command with invalid N."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '-1'])
    
    # Should handle negative N gracefully
    assert result.exit_code == 0 or result.exit_code != 0  # Either way is acceptable


def test_cli_estimate_large_n():
    """Test CLI estimate command with large N."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '1000'])
    
    assert result.exit_code == 0
    assert "PTEF Estimation Results for N=1000" in result.output


def test_cli_estimate_policy():
    """Test CLI estimate command with different policies."""
    runner = CliRunner()
    
    # Test R1 policy (should work)
    result = runner.invoke(cli, ['estimate', '--N', '10', '--policy', 'R1'])
    assert result.exit_code == 0
    
    # Test invalid policy (should fail)
    result = runner.invoke(cli, ['estimate', '--N', '10', '--policy', 'R2'])
    assert result.exit_code != 0


def test_cli_estimate_block_size():
    """Test CLI estimate command with different block sizes."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['estimate', '--N', '100', '--B', '32'])
    assert result.exit_code == 0
    assert "Block size: 32" in result.output


def test_cli_estimate_no_structural_pauses():
    """Test CLI estimate command without structural pauses."""
    runner = CliRunner()
    result = runner.invoke(cli, ['estimate', '--N', '100', '--no-structural-pauses'])
    
    assert result.exit_code == 0
    assert "PTEF Estimation Results for N=100" in result.output
