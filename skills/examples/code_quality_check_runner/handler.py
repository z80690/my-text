# -*- coding: utf-8 -*-
"""Code Quality Check Runner Skill.

Runs comprehensive code quality checks for the project including ESLint,
Prettier format checking, and Pylint analysis.
"""

import subprocess
import re
from typing import Any, Dict, List, Tuple


def run_command(command: str, cwd: str = None) -> Tuple[bool, str, str]:
    """Run a shell command and return success status, stdout, and stderr.

    Args:
        command: Command to execute.
        cwd: Working directory for the command.

    Returns:
        Tuple of (success, stdout, stderr).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out after 120 seconds"
    except Exception as e:
        return False, "", str(e)


def parse_eslint_output(output: str) -> Dict[str, int]:
    """Parse ESLint output to extract error and warning counts.

    Args:
        output: ESLint command output.

    Returns:
        Dict with 'errors' and 'warnings' counts.
    """
    result = {"errors": 0, "warnings": 0}

    # ESLint format patterns
    # Pattern 1: "X errors, Y warnings"
    match = re.search(r'(\d+)\s+errors?,?\s*(\d+)?\s*warnings?', output, re.IGNORECASE)
    if match:
        result["errors"] = int(match.group(1))
        result["warnings"] = int(match.group(2) or 0)

    # Pattern 2: Summary line at end
    summary_match = re.search(r'✖\s+(\d+)\s+error', output)
    if summary_match:
        result["errors"] = int(summary_match.group(1))

    warning_match = re.search(r'⚠\s+(\d+)\s+warning', output)
    if warning_match:
        result["warnings"] = int(warning_match.group(1))

    return result


def parse_prettier_output(output: str, success: bool) -> Dict[str, Any]:
    """Parse Prettier output to determine formatting status.

    Args:
        output: Prettier command output.
        success: Whether the command succeeded.

    Returns:
        Dict with 'passed' status and any issues.
    """
    # Prettier returns exit code 1 when files need formatting
    if success:
        return {"passed": True, "issues": 0}

    # Check for various prettier output patterns
    # Pattern 1: "Would reorder" message
    if "Would reorder" in output:
        return {"passed": False, "issues": 1}

    # Pattern 2: "diff" indicator
    if "diff" in output.lower():
        return {"passed": False, "issues": 1}

    # Pattern 3: File list indicating formatting needed
    if "files" in output.lower() and ("formatted" in output.lower() or "check" in output.lower()):
        return {"passed": False, "issues": 1}

    # If command failed but no clear pattern, assume formatting issues exist
    return {"passed": False, "issues": 1}


def parse_pylint_output(output: str) -> Dict[str, Any]:
    """Parse Pylint output to extract rating and issue counts.

    Args:
        output: Pylint command output.

    Returns:
        Dict with 'rating', 'issues', and other metrics.
    """
    result = {"rating": "0.00/10", "issues": 0, "errors": 0, "warnings": 0, "conventions": 0, "refactors": 0}

    # Extract rating from Pylint output
    # Format: "Your code has been rated at 8.50/10"
    rating_match = re.search(r'rated at\s+([\d.]+)/10', output)
    if rating_match:
        result["rating"] = f"{rating_match.group(1)}/10"

    # Count issues by category
    error_match = re.search(r'(\d+)\s+error', output, re.IGNORECASE)
    if error_match:
        result["errors"] = int(error_match.group(1))

    warning_match = re.search(r'(\d+)\s+warning', output, re.IGNORECASE)
    if warning_match:
        result["warnings"] = int(warning_match.group(1))

    convention_match = re.search(r'(\d+)\s+convention', output, re.IGNORECASE)
    if convention_match:
        result["conventions"] = int(convention_match.group(1))

    refactor_match = re.search(r'(\d+)\s+refactor', output, re.IGNORECASE)
    if refactor_match:
        result["refactors"] = int(refactor_match.group(1))

    # Total issues
    result["issues"] = result["errors"] + result["warnings"] + result["conventions"] + result["refactors"]

    return result


def run_quality_checks() -> Dict[str, Any]:
    """Run all quality checks and compile results.

    Returns:
        Dict with comprehensive quality check results.
    """
    backend_path = "C:\\Users\\Administrator\\Desktop\\my-text\\backend"

    results = {
        "eslint": {"errors": 0, "warnings": 0},
        "prettier": {"passed": True, "issues": 0},
        "pylint": {"rating": "0.00/10", "issues": 0}
    }

    # Run ESLint
    print("[INFO] Running ESLint...")
    eslint_success, eslint_stdout, eslint_stderr = run_command(
        "npm run lint",
        cwd=backend_path
    )
    eslint_result = parse_eslint_output(eslint_stdout + eslint_stderr)
    results["eslint"] = eslint_result
    print(f"[INFO] ESLint: {eslint_result['errors']} errors, {eslint_result['warnings']} warnings")

    # Run Prettier check
    print("[INFO] Running Prettier...")
    prettier_success, prettier_stdout, prettier_stderr = run_command(
        "npm run format:check",
        cwd=backend_path
    )
    prettier_result = parse_prettier_output(prettier_stdout + prettier_stderr, prettier_success)
    results["prettier"] = prettier_result
    print(f"[INFO] Prettier: {'PASSED' if prettier_result['passed'] else 'FAILED'}")

    # Run Pylint
    print("[INFO] Running Pylint...")
    pylint_success, pylint_stdout, pylint_stderr = run_command(
        "npm run lint:python",
        cwd=backend_path
    )
    pylint_result = parse_pylint_output(pylint_stdout + pylint_stderr)
    results["pylint"] = pylint_result
    print(f"[INFO] Pylint: {pylint_result['rating']} ({pylint_result['issues']} issues)")

    return results


def generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on quality check results.

    Args:
        results: Quality check results.

    Returns:
        List of recommendation strings.
    """
    recommendations = []

    # ESLint recommendations
    if results["eslint"]["errors"] > 0:
        recommendations.append(f"Fix {results['eslint']['errors']} ESLint error(s) by running 'npm run lint:fix'")
    if results["eslint"]["warnings"] > 0:
        recommendations.append(f"Review {results['eslint']['warnings']} ESLint warning(s) for potential issues")

    # Prettier recommendations
    if not results["prettier"]["passed"]:
        recommendations.append("Run 'npm run format' to fix formatting issues")

    # Pylint recommendations
    rating_str = results["pylint"]["rating"]
    try:
        rating = float(rating_str.split("/")[0])
        if rating < 7:
            recommendations.append("Pylint rating is below 7/10 - consider refactoring for better code quality")
        if results["pylint"]["errors"] > 0:
            recommendations.append(f"Fix {results['pylint']['errors']} Pylint error(s)")
        if results["pylint"]["warnings"] > 0:
            recommendations.append(f"Review {results['pylint']['warnings']} Pylint warning(s)")
    except (ValueError, IndexError):
        pass

    if not recommendations:
        recommendations.append("Code quality checks passed - great job!")

    return recommendations


def calculate_total_issues(results: Dict[str, Any]) -> int:
    """Calculate total issues from all checks.

    Args:
        results: Quality check results.

    Returns:
        Total count of issues.
    """
    total = 0
    total += results["eslint"]["errors"] + results["eslint"]["warnings"]
    if not results["prettier"]["passed"]:
        total += results["prettier"].get("issues", 1)
    total += results["pylint"]["issues"]
    return total


def handle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the code quality check runner skill.

    Args:
        input_data: Input parameters (optional).
            - check_type: Specific check to run ('eslint', 'prettier', 'pylint', or None for all)

    Returns:
        dict: Quality check results with status, summary, and recommendations.
    """
    from skills.utils import validate_input, format_response

    print("[INFO] Code Quality Check Runner started")

    try:
        results = run_quality_checks()

        total_issues = calculate_total_issues(results)

        overall_status = "passed" if total_issues == 0 else "failed"

        recommendations = generate_recommendations(results)

        output = {
            "status": overall_status,
            "summary": {
                "eslint": results["eslint"],
                "prettier": results["prettier"],
                "pylint": results["pylint"]
            },
            "total_issues": total_issues,
            "recommendations": recommendations
        }

        print(f"[INFO] Quality check completed: {overall_status} ({total_issues} issues)")

        return format_response(True, data=output)

    except Exception as e:
        print(f"[ERROR] Quality check failed: {str(e)}")
        return format_response(False, error=str(e))


if __name__ == "__main__":
    result = handle({})
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
