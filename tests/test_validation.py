import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from utils.validation import (
    ValidationError,
    validate_required_columns,
    validate_numeric_columns,
    validate_no_missing_critical,
    validate_file_not_empty,
)

class TestValidateRequiredColumns:
    def test_all_present(self):
        df = pd.DataFrame({"CENTRAL": ["A"], "GENERADOR": ["B"]})
        validate_required_columns(df, ["CENTRAL", "GENERADOR"])

    def test_missing_column(self):
        df = pd.DataFrame({"CENTRAL": ["A"]})
        with pytest.raises(ValidationError):
            validate_required_columns(df, ["CENTRAL", "GENERADOR"])

class TestValidateNumericColumns:
    def test_already_numeric(self):
        df = pd.DataFrame({"VALOR": [1.0, 2.0]})
        validate_numeric_columns(df, ["VALOR"])

    def test_coercible_to_numeric(self):
        df = pd.DataFrame({"VALOR": ["1,234", "5,678"]})
        validate_numeric_columns(df, ["VALOR"])

    def test_non_numeric(self):
        df = pd.DataFrame({"VALOR": ["abc", "def"]})
        with pytest.raises(ValidationError):
            validate_numeric_columns(df, ["VALOR"])

class TestValidateNoMissingCritical:
    def test_no_missing(self):
        df = pd.DataFrame({"CENTRAL": ["A", "B"]})
        validate_no_missing_critical(df, ["CENTRAL"])

    def test_has_missing(self):
        df = pd.DataFrame({"CENTRAL": ["A", None]})
        with pytest.raises(ValidationError):
            validate_no_missing_critical(df, ["CENTRAL"])

class TestValidateFileNotEmpty:
    def test_file_not_found(self):
        with pytest.raises(ValidationError):
            validate_file_not_empty(Path("/nonexistent/file.xlsx"))
