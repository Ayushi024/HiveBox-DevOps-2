"""
Unit test for verifying the application version output.
"""

import subprocess


def test_version():
    """Test that app_version.py prints the correct version in JSON format."""
    result = subprocess.run(
        ["python", "basic_versioning/app_version.py"], capture_output=True, text=True, check=True
    )
    assert result.returncode == 0
    assert '{"version":' in result.stdout  # Ensure JSON response format
