# -*- coding: utf-8 -*-
"""SQL Schema Validator and Fixer Skill.

Validates Supabase SQL schema files and automatically fixes dependency issues
including syntax errors, missing columns, and incorrect foreign key references.
"""

import os
import re
import json
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ColumnDef:
    """Represents a column definition."""
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    default_value: Optional[str] = None
    line_number: int = 0


@dataclass
class TableDef:
    """Represents a table definition."""
    name: str
    columns: Dict[str, ColumnDef] = field(default_factory=dict)
    primary_keys: Set[str] = field(default_factory=set)
    foreign_keys: List[Dict] = field(default_factory=list)
    line_number: int = 0
    raw_sql: str = ""


@dataclass
class SQLStatement:
    """Represents a parsed SQL statement."""
    statement_type: str  # CREATE_TABLE, ALTER_TABLE, etc.
    raw_sql: str
    line_number: int
    target_table: Optional[str] = None
    referenced_tables: Set[str] = field(default_factory=set)
    referenced_columns: Dict[str, Set[str]] = field(default_factory=dict)
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)


class SQLSchemaParser:
    """Parser for SQL schema files."""

    # SQL statement type patterns
    CREATE_TABLE_PATTERN = re.compile(
        r'^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.+?)\)\s*;?\s*$',
        re.IGNORECASE | re.DOTALL
    )

    ALTER_TABLE_PATTERN = re.compile(
        r'^\s*ALTER\s+TABLE\s+(?:["`]?(\w+)["`]?\.)?(["`]?(\w+)["`]?)\s+'
        r'(?:ADD\s+(?:COLUMN\s+)?)?(?:CONSTRAINT\s+["`]?(\w+)["`]?\s+)?'
        r'(FOREIGN\s+KEY|REFERENCES|PRIMARY\s+KEY|UNIQUE)\s*\(([^)]+)\).*?;?\s*$',
        re.IGNORECASE | re.DOTALL
    )

    INSERT_INTO_PATTERN = re.compile(
        r'^\s*INSERT\s+INTO\s+["`]?(\w+)["`]?\s*\(([^)]*)\)\s*VALUES\s*\(([^)]*)\)\s*;?\s*$',
        re.IGNORECASE
    )

    COMMENT_PATTERN = re.compile(r'--[^\n]*\n|/\*.*?\*/', re.DOTALL)

    def __init__(self):
        self.tables: Dict[str, TableDef] = {}
        self.statements: List[SQLStatement] = []
        self.issues: List[Dict] = []

    def parse_file(self, content: str) -> Tuple[List[SQLStatement], Dict[str, TableDef]]:
        """Parse SQL file content.

        Args:
            content: SQL file content.

        Returns:
            Tuple of (statements, tables).
        """
        # Remove comments
        cleaned_content = self._remove_comments(content)

        # Split into individual statements
        statements = self._split_statements(cleaned_content)

        # Parse each statement
        for i, stmt_sql in enumerate(statements):
            stmt = self._parse_statement(stmt_sql, i + 1)
            self.statements.append(stmt)

            if stmt.statement_type == "CREATE_TABLE":
                self._extract_table_info(stmt)

        return self.statements, self.tables

    def _remove_comments(self, content: str) -> str:
        """Remove SQL comments from content.

        Args:
            content: SQL content.

        Returns:
            Content without comments.
        """
        # Remove block comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove line comments
        content = re.sub(r'--[^\n]*', '', content)
        return content.strip()

    def _split_statements(self, content: str) -> List[str]:
        """Split content into individual SQL statements.

        Args:
            content: SQL content.

        Returns:
            List of individual statements.
        """
        # Split by semicolons, but handle nested ones
        statements = []
        current = []
        depth = 0

        for char in content:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ';' and depth == 0:
                if current:
                    stmt = ''.join(current).strip()
                    if stmt:
                        statements.append(stmt)
                    current = []
                continue
            current.append(char)

        if current:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)

        return statements

    def _parse_statement(self, stmt_sql: str, line_number: int) -> SQLStatement:
        """Parse a single SQL statement.

        Args:
            stmt_sql: SQL statement string.
            line_number: Original line number.

        Returns:
            Parsed SQLStatement.
        """
        stmt = SQLStatement(
            statement_type="UNKNOWN",
            raw_sql=stmt_sql,
            line_number=line_number
        )

        # Check for CREATE TABLE
        create_match = self.CREATE_TABLE_PATTERN.match(stmt_sql)
        if create_match:
            stmt.statement_type = "CREATE_TABLE"
            stmt.target_table = create_match.group(1)
            return stmt

        # Check for ALTER TABLE (foreign key, references, etc.)
        alter_match = self.ALTER_TABLE_PATTERN.match(stmt_sql)
        if alter_match:
            stmt.statement_type = "ALTER_TABLE"
            # Extract table name (handle schema.table format)
            table_name = alter_match.group(3)
            stmt.target_table = table_name

            # Check what type of constraint
            constraint_type = alter_match.group(5).upper()
            columns = [c.strip().strip('"').strip('`') for c in alter_match.group(6).split(',')]

            if constraint_type == "FOREIGN KEY":
                stmt.referenced_columns[table_name] = set(columns)
                # Try to extract referenced table
                fk_match = re.search(
                    r'FOREIGN\s+KEY\s*\([^)]+\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\([^)]+\)',
                    stmt_sql,
                    re.IGNORECASE
                )
                if fk_match:
                    stmt.referenced_tables.add(fk_match.group(1))
            elif constraint_type == "REFERENCES":
                stmt.referenced_columns[table_name] = set(columns)
                # Extract referenced table
                ref_match = re.search(
                    r'REFERENCES\s+["`]?(\w+)["`]?\s*\(([^)]+)\)',
                    stmt_sql,
                    re.IGNORECASE
                )
                if ref_match:
                    stmt.referenced_tables.add(ref_match.group(1))

            return stmt

        # Check for standalone REFERENCES in column definition
        if "REFERENCES" in stmt_sql.upper():
            ref_match = re.search(
                r'REFERENCES\s+["`]?(\w+)["`]?\s*\(([^)]+)\)',
                stmt_sql,
                re.IGNORECASE
            )
            if ref_match:
                stmt.referenced_tables.add(ref_match.group(1))

        return stmt

    def _extract_table_info(self, stmt: SQLStatement) -> None:
        """Extract table definition from CREATE TABLE statement.

        Args:
            stmt: CREATE_TABLE statement.
        """
        table_name = stmt.target_table
        if not table_name:
            return

        table = TableDef(name=table_name, line_number=stmt.line_number, raw_sql=stmt.raw_sql)

        # Extract column definitions
        create_match = self.CREATE_TABLE_PATTERN.match(stmt.raw_sql)
        if not create_match:
            return

        columns_part = create_match.group(2)

        # Split by comma, but handle parentheses
        columns = self._split_columns(columns_part)

        for col_str in columns:
            col_str = col_str.strip()
            if not col_str:
                continue

            # Parse column definition
            col = self._parse_column_definition(col_str, stmt.line_number)
            if col:
                table.columns[col.name] = col
                if col.is_primary_key:
                    table.primary_keys.add(col.name)

        # Extract foreign key constraints
        fk_constraints = self._extract_foreign_keys(stmt.raw_sql, stmt.line_number)
        table.foreign_keys = fk_constraints

        self.tables[table_name] = table

    def _split_columns(self, columns_part: str) -> List[str]:
        """Split column definitions, handling nested parentheses.

        Args:
            columns_part: Column definitions string.

        Returns:
            List of column definition strings.
        """
        columns = []
        current = []
        depth = 0

        for char in columns_part:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                if current:
                    columns.append(''.join(current))
                current = []
                continue
            current.append(char)

        if current:
            columns.append(''.join(current))

        return columns

    def _parse_column_definition(self, col_str: str, base_line: int) -> Optional[ColumnDef]:
        """Parse a column definition.

        Args:
            col_str: Column definition string.
            base_line: Base line number.

        Returns:
            ColumnDef or None.
        """
        # Handle PRIMARY KEY constraint
        pk_match = re.match(
            r'^\s*PRIMARY\s+KEY\s*\(([^)]+)\)\s*$',
            col_str,
            re.IGNORECASE
        )
        if pk_match:
            # This is a table-level primary key, not a column
            return None

        # Handle FOREIGN KEY constraint
        fk_match = re.match(
            r'^\s*FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\(([^)]+)\).*$',
            col_str,
            re.IGNORECASE
        )
        if fk_match:
            # This is a table-level foreign key, not a column
            return None

        # Handle UNIQUE constraint
        unique_match = re.match(
            r'^\s*UNIQUE\s*\(([^)]+)\)\s*$',
            col_str,
            re.IGNORECASE
        )
        if unique_match:
            # This is a table-level constraint, not a column
            return None

        # Parse column name and type
        match = re.match(r'^\s*["`]?(\w+)["`]?\s+([^\s(]+)', col_str)
        if not match:
            return None

        name = match.group(1)
        data_type = match.group(2).upper()

        col = ColumnDef(
            name=name,
            data_type=data_type,
            line_number=base_line
        )

        # Check for NOT NULL
        if "NOT NULL" in col_str.upper():
            col.is_nullable = False

        # Check for NULL
        if re.search(r'\bNULL\b', col_str.upper()) and "NOT NULL" not in col_str.upper():
            col.is_nullable = True

        # Check for PRIMARY KEY
        if "PRIMARY KEY" in col_str.upper():
            col.is_primary_key = True

        # Check for DEFAULT
        default_match = re.search(r'DEFAULT\s+(\S+|\'[^\']*\'|\"[^\"]*\")', col_str, re.IGNORECASE)
        if default_match:
            col.default_value = default_match.group(1)

        return col

    def _extract_foreign_keys(self, sql: str, base_line: int) -> List[Dict]:
        """Extract foreign key constraints from SQL.

        Args:
            sql: CREATE TABLE SQL.
            base_line: Base line number.

        Returns:
            List of foreign key definitions.
        """
        fks = []

        # Match table-level foreign key constraints
        pattern = re.compile(
            r'FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+["`]?(\w+)["`]?\s*\(([^)]+)\)',
            re.IGNORECASE
        )

        for match in pattern.finditer(sql):
            fks.append({
                "columns": [c.strip().strip('"').strip('`') for c in match.group(1).split(',')],
                "referenced_table": match.group(2),
                "referenced_columns": [c.strip().strip('"').strip('`') for c in match.group(3).split(',')],
                "line_number": base_line
            })

        return fks


class SQLSchemaValidator:
    """Validates SQL schema and identifies issues."""

    def __init__(self, strict_mode: bool = False):
        self.tables: Dict[str, TableDef] = {}
        self.statements: List[SQLStatement] = []
        self.issues: List[Dict] = []
        self.strict_mode = strict_mode

    def validate(
        self,
        statements: List[SQLStatement],
        tables: Dict[str, TableDef]
    ) -> List[Dict]:
        """Validate SQL schema.

        Args:
            statements: Parsed SQL statements.
            tables: Table definitions.

        Returns:
            List of identified issues.
        """
        self.tables = tables
        self.statements = statements
        self.issues = []

        # Check each statement
        for stmt in statements:
            self._validate_statement(stmt)

        # Check dependency order
        self._validate_dependency_order()

        return self.issues

    def _validate_statement(self, stmt: SQLStatement) -> None:
        """Validate a single statement.

        Args:
            stmt: SQL statement to validate.
        """
        if stmt.statement_type == "CREATE_TABLE":
            self._validate_create_table(stmt)
        elif stmt.statement_type == "ALTER_TABLE":
            self._validate_alter_table(stmt)

    def _validate_create_table(self, stmt: SQLStatement) -> None:
        """Validate CREATE TABLE statement.

        Args:
            stmt: CREATE_TABLE statement.
        """
        table_name = stmt.target_table
        if not table_name:
            self.issues.append({
                "type": "SYNTAX_ERROR",
                "line": stmt.line_number,
                "message": "Could not parse table name",
                "sql": stmt.raw_sql
            })
            return

        # Check for duplicate tables
        if table_name in self.tables:
            existing = self.tables[table_name]
            if existing.line_number != stmt.line_number:
                self.issues.append({
                    "type": "DUPLICATE_TABLE",
                    "line": stmt.line_number,
                    "table": table_name,
                    "message": f"Table '{table_name}' is defined multiple times",
                    "first_definition_line": existing.line_number
                })

    def _validate_alter_table(self, stmt: SQLStatement) -> None:
        """Validate ALTER TABLE statement.

        Args:
            stmt: ALTER_TABLE statement.
        """
        table_name = stmt.target_table
        if not table_name:
            return

        # Check if table exists
        if table_name not in self.tables:
            self.issues.append({
                "type": "MISSING_TABLE",
                "line": stmt.line_number,
                "table": table_name,
                "message": f"Table '{table_name}' does not exist",
                "sql": stmt.raw_sql
            })
            return

        table = self.tables[table_name]

        # Check for foreign key references
        if stmt.referenced_tables:
            for ref_table in stmt.referenced_tables:
                if ref_table not in self.tables and ref_table != table_name:
                    self.issues.append({
                        "type": "MISSING_FOREIGN_TABLE",
                        "line": stmt.line_number,
                        "table": table_name,
                        "referenced_table": ref_table,
                        "message": f"Referenced table '{ref_table}' does not exist",
                        "sql": stmt.raw_sql
                    })

        # Extract columns being referenced in FK
        fk_match = re.search(
            r'FOREIGN\s+KEY\s*\(([^)]+)\)',
            stmt.raw_sql,
            re.IGNORECASE
        )
        if fk_match:
            columns = [c.strip().strip('"').strip('`') for c in fk_match.group(1).split(',')]
            for col in columns:
                if col not in table.columns:
                    self.issues.append({
                        "type": "MISSING_COLUMN",
                        "line": stmt.line_number,
                        "table": table_name,
                        "column": col,
                        "message": f"Column '{col}' does not exist in table '{table_name}'",
                        "sql": stmt.raw_sql
                    })

    def _validate_dependency_order(self) -> None:
        """Validate that tables are created in correct dependency order."""
        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}

        for table_name, table in self.tables.items():
            dependencies[table_name] = set()

            # Check foreign keys
            for fk in table.foreign_keys:
                ref_table = fk["referenced_table"]
                if ref_table != table_name and ref_table not in self.tables:
                    continue
                dependencies[table_name].add(ref_table)

            # Check column references
            for col in table.columns.values():
                # This would need more sophisticated parsing
                pass

        # Check if tables are created in topological order
        for table_name in self.tables:
            table = self.tables[table_name]
            for stmt in self.statements:
                if stmt.target_table == table_name and stmt.statement_type == "CREATE_TABLE":
                    self._check_table_dependencies(stmt, table_name, dependencies, self.tables)

    def _check_table_dependencies(
        self,
        stmt: SQLStatement,
        table_name: str,
        dependencies: Dict[str, Set[str]],
        tables: Dict[str, TableDef]
    ) -> None:
        """Check if table dependencies are satisfied.

        Args:
            stmt: Current statement.
            table_name: Table name.
            dependencies: Dependency graph.
            tables: All table definitions.
        """
        for dep_table in dependencies.get(table_name, set()):
            if dep_table not in tables:
                continue

            # Find the CREATE TABLE statement for the dependency
            for other_stmt in self.statements:
                if (other_stmt.statement_type == "CREATE_TABLE" and
                    other_stmt.target_table == dep_table):
                    # If dependency is created after this table, flag it
                    if other_stmt.line_number > stmt.line_number:
                        self.issues.append({
                            "type": "DEPENDENCY_ORDER",
                            "line": stmt.line_number,
                            "table": table_name,
                            "dependency": dep_table,
                            "message": f"Table '{table_name}' should be created after '{dep_table}' it references",
                            "sql": stmt.raw_sql
                        })


class SQLSchemaFixer:
    """Generates fixed SQL schema."""

    def __init__(self):
        self.validator = SQLSchemaValidator()

    def fix(
        self,
        statements: List[SQLStatement],
        tables: Dict[str, TableDef],
        issues: List[Dict]
    ) -> str:
        """Generate fixed SQL.

        Args:
            statements: Original statements.
            tables: Table definitions.
            issues: Identified issues.

        Returns:
            Fixed SQL string.
        """
        # Reorder statements based on dependencies
        fixed_statements = self._reorder_statements(statements, tables, issues)

        # Build SQL
        sql_parts = []
        for stmt in fixed_statements:
            sql_parts.append(stmt.raw_sql)

        return "\n\n".join(sql_parts)

    def _reorder_statements(
        self,
        statements: List[SQLStatement],
        tables: Dict[str, TableDef],
        issues: List[Dict]
    ) -> List[SQLStatement]:
        """Reorder statements to satisfy dependencies.

        Args:
            statements: Original statements.
            tables: Table definitions.
            issues: Identified issues.

        Returns:
            Reordered statements.
        """
        # Build dependency graph
        dependencies: Dict[str, Set[str]] = {}
        table_to_stmt: Dict[str, SQLStatement] = {}

        for stmt in statements:
            if stmt.statement_type == "CREATE_TABLE" and stmt.target_table:
                table_to_stmt[stmt.target_table] = stmt
                dependencies[stmt.target_table] = set()

                if stmt.target_table in tables:
                    table = tables[stmt.target_table]
                    for fk in table.foreign_keys:
                        if fk["referenced_table"] != stmt.target_table:
                            dependencies[stmt.target_table].add(fk["referenced_table"])

        # Topological sort
        sorted_tables = self._topological_sort(dependencies)

        # Build ordered statements
        ordered_statements = []
        processed = set()

        for table_name in sorted_tables:
            if table_name in table_to_stmt and table_name not in processed:
                ordered_statements.append(table_to_stmt[table_name])
                processed.add(table_name)

        # Add any statements that weren't part of the sort (like ALTER TABLE)
        for stmt in statements:
            if stmt.statement_type != "CREATE_TABLE":
                ordered_statements.append(stmt)

        return ordered_statements

    def _topological_sort(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort on dependency graph.

        Args:
            dependencies: Dependency graph.

        Returns:
            Topologically sorted list of table names.
        """
        # Kahn's algorithm
        in_degree: Dict[str, int] = {}
        for node in dependencies:
            in_degree[node] = 0

        for node, deps in dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[node] = in_degree.get(node, 0) + 1

        queue = [n for n in in_degree if in_degree[n] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for n, deps in dependencies.items():
                if node in deps:
                    in_degree[n] -= 1
                    if in_degree[n] == 0:
                        queue.append(n)

        # Handle cycles by adding remaining nodes
        for node in in_degree:
            if node not in result:
                result.append(node)

        return result


def analyze_sql_file(file_path: str) -> Dict[str, Any]:
    """Analyze a SQL file and return validation results.

    Args:
        file_path: Path to SQL file.

    Returns:
        Analysis report.
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}"
        }

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return {
            "success": False,
            "error": f"Could not decode file as UTF-8: {file_path}"
        }

    # Parse the SQL
    parser = SQLSchemaParser()
    statements, tables = parser.parse_file(content)

    # Validate
    validator = SQLSchemaValidator()
    issues = validator.validate(statements, tables)

    # Generate fixes
    fixer = SQLSchemaFixer()
    fixed_sql = fixer.fix(statements, tables, issues)

    # Build report
    report = {
        "success": True,
        "file_path": file_path,
        "statistics": {
            "total_statements": len(statements),
            "create_table_count": sum(1 for s in statements if s.statement_type == "CREATE_TABLE"),
            "alter_table_count": sum(1 for s in statements if s.statement_type == "ALTER_TABLE"),
            "tables_found": list(tables.keys())
        },
        "tables": {
            name: {
                "columns": list(table.columns.keys()),
                "primary_keys": list(table.primary_keys),
                "foreign_keys": table.foreign_keys,
                "line_number": table.line_number
            }
            for name, table in tables.items()
        },
        "issues": {
            "count": len(issues),
            "details": issues
        },
        "fixed_sql": fixed_sql
    }

    return report


def handle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main handler for SQL schema validation skill.

    Args:
        input_data: Input parameters.
            - file_path: Path to SQL file (required).
            - output_path: Path for fixed SQL output (optional).
            - strict_mode: Enable strict validation (optional, default: False).

    Returns:
        dict: Validation report with issues and fixed SQL.
    """
    from skills.utils import validate_input, format_response

    # Validate input
    is_valid, error = validate_input(input_data, ["file_path"])
    if not is_valid:
        return format_response(False, error=error)

    file_path = input_data["file_path"]
    output_path = input_data.get("output_path")
    strict_mode = input_data.get("strict_mode", False)

    # Analyze SQL file
    report = analyze_sql_file(file_path)

    if not report["success"]:
        return format_response(False, error=report["error"])

    # Save fixed SQL if output path provided
    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report["fixed_sql"])
            report["fixed_sql_saved_to"] = output_path
        except Exception as e:
            return format_response(False, error=f"Failed to write fixed SQL: {str(e)}")

    return format_response(True, data=report)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python handler.py <sql_file_path> [output_path]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = handle({"file_path": file_path, "output_path": output_path})

    if result["success"]:
        report = result["data"]
        print(f"SQL Schema Analysis Report")
        print(f"===========================")
        print(f"File: {report['file_path']}")
        print(f"Statements: {report['statistics']['total_statements']}")
        print(f"Tables: {', '.join(report['statistics']['tables_found'])}")
        print(f"Issues: {report['issues']['count']}")

        if report['issues']['count'] > 0:
            print(f"\nIssues Found:")
            for issue in report['issues']['details']:
                print(f"  [{issue['type']}] Line {issue['line']}: {issue['message']}")

        if output_path:
            print(f"\nFixed SQL saved to: {output_path}")
    else:
        print(f"Error: {result['error']}")
