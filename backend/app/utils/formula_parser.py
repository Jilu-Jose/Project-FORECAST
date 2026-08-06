"""Excel formula tokenization and cell reference extraction.

Uses openpyxl's Tokenizer to parse formulas, extract precedent cell refs,
detect hardcoded constants within formulas, and normalize cross-sheet references.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from openpyxl.formula.tokenizer import Token, Tokenizer
from openpyxl.utils import get_column_letter, column_index_from_string


@dataclass
class CellReference:
    """A parsed cell reference, possibly cross-sheet."""
    sheet: str | None  # None = same sheet
    cell: str          # e.g. "B5" or "B5:B10"
    is_range: bool = False

    @property
    def absolute(self) -> str:
        """Return fully qualified reference."""
        if self.sheet:
            return f"'{self.sheet}'!{self.cell}"
        return self.cell


@dataclass
class FormulaInfo:
    """Parsed information from a single cell's formula."""
    raw_formula: str
    precedent_refs: list[CellReference] = field(default_factory=list)
    hardcoded_numbers: list[float] = field(default_factory=list)
    function_names: list[str] = field(default_factory=list)
    has_error: bool = False
    error_type: str | None = None


# Common Excel error values
ERROR_VALUES = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#NULL!", "#N/A", "#NUM!"}

# Regex for cell references like A1, $A$1, Sheet1!A1, 'Sheet Name'!A1
CELL_REF_PATTERN = re.compile(
    r"(?:'([^']+)'|(\w+))!"  # optional sheet part
    r"(\$?[A-Z]{1,3}\$?\d+)"  # cell reference
    r"(?::(\$?[A-Z]{1,3}\$?\d+))?",  # optional range end
    re.IGNORECASE,
)

SIMPLE_CELL_PATTERN = re.compile(
    r"(\$?[A-Z]{1,3}\$?\d+)(?::(\$?[A-Z]{1,3}\$?\d+))?",
    re.IGNORECASE,
)


def parse_formula(formula: str, current_sheet: str | None = None) -> FormulaInfo:
    """Parse an Excel formula string and extract its components.

    Args:
        formula: The formula string (with or without leading '=')
        current_sheet: The sheet containing this formula (for resolving relative refs)

    Returns:
        FormulaInfo with extracted precedent refs, hardcoded numbers, and function names.
    """
    info = FormulaInfo(raw_formula=formula)

    if not formula:
        return info

    # Check for error values
    formula_upper = formula.upper().strip()
    for err in ERROR_VALUES:
        if err in formula_upper:
            info.has_error = True
            info.error_type = err
            # Don't return early — still parse what we can

    # Strip leading '='
    formula_text = formula.lstrip("=")

    try:
        tok = Tokenizer(formula)
    except Exception:
        # If tokenizer fails, fall back to regex parsing
        return _regex_fallback_parse(formula, current_sheet, info)

    for token in tok.items:
        if token.type == Token.OPERAND:
            if token.subtype == Token.RANGE:
                # Cell reference
                ref = _parse_cell_token(token.value, current_sheet)
                if ref:
                    info.precedent_refs.append(ref)
            elif token.subtype == Token.NUMBER:
                # Hardcoded numeric constant
                try:
                    info.hardcoded_numbers.append(float(token.value))
                except ValueError:
                    pass
        elif token.type == Token.FUNC and token.subtype == Token.OPEN:
            # Function name (strip trailing '(')
            func_name = token.value.rstrip("(").upper()
            if func_name:
                info.function_names.append(func_name)

    return info


def _parse_cell_token(value: str, current_sheet: str | None) -> CellReference | None:
    """Parse a token value into a CellReference."""
    value = value.strip()

    # Try cross-sheet reference first: 'Sheet1'!A1 or Sheet1!A1
    match = CELL_REF_PATTERN.match(value)
    if match:
        sheet = match.group(1) or match.group(2)
        cell = match.group(3)
        end_cell = match.group(4)
        cell_str = f"{cell}:{end_cell}" if end_cell else cell
        return CellReference(sheet=sheet, cell=_normalize_cell(cell_str), is_range=bool(end_cell))

    # Simple reference: A1 or A1:B5
    match = SIMPLE_CELL_PATTERN.match(value)
    if match:
        cell = match.group(1)
        end_cell = match.group(2)
        cell_str = f"{cell}:{end_cell}" if end_cell else cell
        return CellReference(
            sheet=current_sheet,
            cell=_normalize_cell(cell_str),
            is_range=bool(end_cell),
        )

    return None


def _normalize_cell(cell_ref: str) -> str:
    """Remove $ signs from cell references for consistent graph keys."""
    return cell_ref.replace("$", "").upper()


def _regex_fallback_parse(
    formula: str, current_sheet: str | None, info: FormulaInfo
) -> FormulaInfo:
    """Fallback parser using regex when openpyxl tokenizer fails."""
    # Find cross-sheet refs
    for match in CELL_REF_PATTERN.finditer(formula):
        sheet = match.group(1) or match.group(2)
        cell = match.group(3)
        end_cell = match.group(4)
        cell_str = f"{cell}:{end_cell}" if end_cell else cell
        info.precedent_refs.append(
            CellReference(sheet=sheet, cell=_normalize_cell(cell_str), is_range=bool(end_cell))
        )

    # Find simple refs (but avoid matching ones already found as cross-sheet)
    remaining = CELL_REF_PATTERN.sub("", formula)
    for match in SIMPLE_CELL_PATTERN.finditer(remaining):
        cell = match.group(1)
        end_cell = match.group(2)
        cell_str = f"{cell}:{end_cell}" if end_cell else cell
        info.precedent_refs.append(
            CellReference(
                sheet=current_sheet,
                cell=_normalize_cell(cell_str),
                is_range=bool(end_cell),
            )
        )

    # Find hardcoded numbers (not part of cell refs)
    for num_match in re.finditer(r"(?<![A-Z])(\d+\.?\d*)", remaining):
        try:
            info.hardcoded_numbers.append(float(num_match.group(1)))
        except ValueError:
            pass

    return info


def expand_range(range_ref: str) -> list[str]:
    """Expand a cell range like 'B2:B10' into individual cell refs.

    Args:
        range_ref: A range string like "B2:B10"

    Returns:
        List of individual cell references.
    """
    if ":" not in range_ref:
        return [range_ref]

    start, end = range_ref.split(":")
    start = _normalize_cell(start)
    end = _normalize_cell(end)

    # Parse column and row
    start_col_str = re.match(r"([A-Z]+)", start).group(1)
    start_row = int(re.search(r"(\d+)", start).group(1))
    end_col_str = re.match(r"([A-Z]+)", end).group(1)
    end_row = int(re.search(r"(\d+)", end).group(1))

    start_col = column_index_from_string(start_col_str)
    end_col = column_index_from_string(end_col_str)

    cells = []
    for col in range(start_col, end_col + 1):
        for row in range(start_row, end_row + 1):
            cells.append(f"{get_column_letter(col)}{row}")

    return cells


def detect_formula_pattern(formulas: list[str]) -> str | None:
    """Detect the dominant pattern in a list of formulas.

    Returns a generalized pattern string, or None if no consistent pattern.
    For example, if most formulas are "=SUM(B2:B5)", the pattern is "SUM(range)".
    """
    if not formulas:
        return None

    patterns = []
    for f in formulas:
        if not f:
            patterns.append("EMPTY")
            continue
        info = parse_formula(f)
        if info.function_names:
            patterns.append(info.function_names[0])
        elif info.precedent_refs and not info.function_names:
            patterns.append("CELL_REF")
        elif not info.precedent_refs and not info.function_names:
            patterns.append("CONSTANT")
        else:
            patterns.append("COMPLEX")

    # Find majority pattern
    if not patterns:
        return None

    from collections import Counter
    counts = Counter(patterns)
    most_common, count = counts.most_common(1)[0]

    if count / len(patterns) >= 0.6:
        return most_common

    return None


def find_pattern_outliers(
    cells: list[tuple[str, str | None]],  # (cell_ref, formula_or_None)
    current_sheet: str,
) -> list[tuple[str, str]]:
    """Find cells whose formula pattern differs from the majority in a row/column group.

    Args:
        cells: List of (cell_ref, formula) tuples from the same row or column
        current_sheet: Sheet name for context

    Returns:
        List of (cell_ref, reason) for outlier cells
    """
    if len(cells) < 3:
        return []

    # Parse all formulas
    parsed = []
    for cell_ref, formula in cells:
        if formula:
            info = parse_formula(formula, current_sheet)
            if info.function_names:
                pattern = info.function_names[0]
            elif info.precedent_refs:
                pattern = "CELL_REF"
            else:
                pattern = "CONSTANT"
        else:
            pattern = "VALUE_ONLY"
        parsed.append((cell_ref, formula, pattern))

    # Find majority
    from collections import Counter
    patterns = [p[2] for p in parsed]
    counts = Counter(patterns)
    majority_pattern, majority_count = counts.most_common(1)[0]

    # Only flag if there's a clear majority (>= 70% of cells)
    if majority_count / len(patterns) < 0.7:
        return []

    outliers = []
    for cell_ref, formula, pattern in parsed:
        if pattern != majority_pattern:
            outliers.append((
                cell_ref,
                f"Expected pattern '{majority_pattern}' but found '{pattern}' "
                f"(formula: {formula or 'none'})"
            ))

    return outliers
