# -*- coding: utf-8 -*-
"""Code Quality Check Skill.

Analyzes Python files for code quality metrics and generates a quality report.
"""

import os
import re
from typing import Any, Dict, List, Tuple


def handle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a Python file for code quality metrics.

    Args:
        input_data: Input parameters containing file_path.
            - file_path: Path to the Python file to analyze (required).

    Returns:
        dict: Quality report containing metrics, issues, and a letter grade.
    """
    from skills.utils import validate_input, format_response

    is_valid, error = validate_input(input_data, ["file_path"])
    if not is_valid:
        return format_response(False, error=error)

    file_path = input_data["file_path"]

    if not os.path.exists(file_path):
        return format_response(False, error=f"File not found: {file_path}")

    if not file_path.endswith(".py"):
        return format_response(False, error="Only Python files are supported")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        report = analyze_code_quality(file_path, lines)

        return format_response(True, data=report)

    except UnicodeDecodeError:
        return format_response(False, error=f"Could not decode file as UTF-8: {file_path}")
    except Exception as e:
        return format_response(False, error=f"Error analyzing file: {str(e)}")


def analyze_code_quality(file_path: str, lines: List[str]) -> Dict[str, Any]:
    """Analyze code and generate quality report.

    Args:
        file_path: Path to the Python file.
        lines: List of lines from the file.

    Returns:
        dict: Quality report with all metrics.
    """
    total_lines = len(lines)
    file_size = sum(len(line) for line in lines)

    issues = []
    issues.extend(check_long_lines(lines))
    issues.extend(check_todo_comments(lines))
    issues.extend(check_unused_imports(lines, file_path))

    avg_function_length = calculate_average_function_length(lines)

    grade = calculate_grade(total_lines, file_size, len(issues), avg_function_length)

    report = {
        "file_path": file_path,
        "file_size_bytes": file_size,
        "total_lines": total_lines,
        "complexity": {
            "average_function_length": avg_function_length,
            "function_count": count_functions(lines),
        },
        "issues": {
            "count": len(issues),
            "details": issues[:10],
        },
        "grade": grade,
    }

    return report


def check_long_lines(lines: List[str], max_length: int = 120) -> List[Dict[str, Any]]:
    """Check for lines that exceed the maximum length.

    Args:
        lines: List of file lines.
        max_length: Maximum allowed line length (default: 120).

    Returns:
        list: List of long line issues.
    """
    issues = []
    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n\r")
        if len(stripped) > max_length:
            issues.append({
                "type": "long_line",
                "line": i,
                "length": len(stripped),
                "max_allowed": max_length,
                "snippet": stripped[:80] + "...",
            })
    return issues


def check_todo_comments(lines: List[str]) -> List[Dict[str, Any]]:
    """Check for TODO and FIXME comments.

    Args:
        lines: List of file lines.

    Returns:
        list: List of TODO/FIXME comments found.
    """
    issues = []
    todo_pattern = re.compile(r"#\s*(TODO|FIXME|HACK|XXX|BUG)", re.IGNORECASE)

    for i, line in enumerate(lines, start=1):
        match = todo_pattern.search(line)
        if match:
            issues.append({
                "type": "todo_comment",
                "line": i,
                "comment_type": match.group(1).upper(),
                "snippet": line.strip(),
            })
    return issues


def check_unused_imports(lines: List[str], file_path: str) -> List[Dict[str, Any]]:
    """Check for potentially unused imports.

    This is a simple heuristic that checks if imported names
    appear only once in the import statement and not elsewhere.

    Args:
        lines: List of file lines.
        file_path: Path to the file (for relative import analysis).

    Returns:
        list: List of potentially unused imports.
    """
    issues = []
    import_pattern = re.compile(r"^(?:from\s+(\S+)\s+import|import\s+(\S+))")
    content = "".join(lines)

    for i, line in enumerate(lines, start=1):
        import_match = import_pattern.match(line)
        if import_match:
            module = import_match.group(1) or import_match.group(2)
            module_name = module.split(".")[-1]
            aliases = parse_import_aliases(line, module_name)

            for alias in aliases:
                if alias["name"] not in content[lines[0:i].__len__():]:
                    issues.append({
                        "type": "unused_import",
                        "line": i,
                        "import_name": alias["name"],
                        "snippet": line.strip(),
                    })

    return issues


def parse_import_aliases(line: str, module_name: str) -> List[Dict[str, str]]:
    """Parse import statement to extract names and aliases.

    Args:
        line: Import statement line.
        module_name: Module name being imported.

    Returns:
        list: List of dicts with name and alias.
    """
    names = []
    if "from" in line:
        match = re.search(rf"from\s+{re.escape(module_name)}\s+import\s+(.+)", line)
        if match:
            imports_str = match.group(1)
            for part in imports_str.split(","):
                part = part.strip()
                if " as " in part:
                    name, alias = part.split(" as ")
                    names.append({"name": name.strip(), "alias": alias.strip()})
                else:
                    names.append({"name": part, "alias": None})
    else:
        for part in module_name.split(","):
            part = part.strip()
            if " as " in part:
                name, alias = part.split(" as ")
                names.append({"name": name.strip(), "alias": alias.strip()})
            else:
                names.append({"name": part, "alias": None})
    return names


def calculate_average_function_length(lines: List[str]) -> float:
    """Calculate average function length.

    Args:
        lines: List of file lines.

    Returns:
        float: Average number of lines per function.
    """
    function_pattern = re.compile(r"^\s*def\s+\w+\s*\([^)]*\)\s*:")
    function_lines = 0
    current_indent = None
    in_function = False

    for line in lines:
        stripped = line.lstrip()
        if function_pattern.match(line):
            in_function = True
            current_indent = len(line) - len(stripped)
            function_lines += 1
        elif in_function:
            indent = len(line) - len(stripped)
            if indent <= current_indent and stripped:
                in_function = False
            else:
                function_lines += 1

    function_count = len(re.findall(r"^\s*def\s+\w+\s*\([^)]*\)\s*:", "".join(lines)))

    if function_count == 0:
        return 0.0

    return round(function_lines / function_count, 1)


def count_functions(lines: List[str]) -> int:
    """Count the number of function definitions.

    Args:
        lines: List of file lines.

    Returns:
        int: Number of function definitions.
    """
    pattern = re.compile(r"^\s*def\s+\w+\s*\([^)]*\)\s*:")
    return sum(1 for line in lines if pattern.match(line))


def calculate_grade(
    total_lines: int,
    file_size: int,
    issue_count: int,
    avg_function_length: float
) -> str:
    """Calculate a letter grade based on quality metrics.

    Args:
        total_lines: Total number of lines in the file.
        file_size: File size in bytes.
        issue_count: Number of issues found.
        avg_function_length: Average function length.

    Returns:
        str: Letter grade (A, B, C, D, or F).
    """
    score = 100

    score -= min(issue_count * 2, 30)

    if total_lines > 500:
        score -= 10
    elif total_lines > 300:
        score -= 5

    if file_size > 50 * 1024:
        score -= 10
    elif file_size > 20 * 1024:
        score -= 5

    if avg_function_length > 50:
        score -= 15
    elif avg_function_length > 30:
        score -= 10
    elif avg_function_length > 20:
        score -= 5

    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python handler.py <python_file_path>")
        sys.exit(1)

    result = handle({"file_path": sys.argv[1]})

    if result["success"]:
        import json
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))
    else:
        print(f"Error: {result['error']}")
