import pytest
from utils.data_loader import build_date_mapping, parse_period_code, resolve_data_path


class TestDateMapping:
    def test_build_date_mapping_keys(self):
        mapping = build_date_mapping(2023, 2023)
        assert "012023" in mapping
        assert "122023" in mapping
        assert len(mapping) == 12

    def test_build_date_mapping_values(self):
        mapping = build_date_mapping(2024, 2024)
        assert mapping["012024"] == "2024-01-01"
        assert mapping["122024"] == "2024-12-01"

    def test_build_date_mapping_multi_year(self):
        mapping = build_date_mapping(2023, 2025)
        assert len(mapping) == 36
        assert "012023" in mapping
        assert "122025" in mapping


class TestParsePeriodCode:
    def test_six_digit_code(self):
        d = parse_period_code("012024")
        assert d is not None
        assert d.year == 2024
        assert d.month == 1

    def test_five_digit_code(self):
        d = parse_period_code("12024")
        assert d is not None
        assert d.year == 2024
        assert d.month == 1

    def test_invalid_code(self):
        assert parse_period_code("") is None
        assert parse_period_code("abc") is None
        assert parse_period_code("1234567") is None


class TestResolveDataPath:
    def test_resolve_data_path(self):
        path = resolve_data_path("data_generacion")
        assert path.exists()
        assert path.name == "data_generacion"

    def test_resolve_data_path_distribuidor(self):
        path = resolve_data_path("data_distribuidor")
        assert path.exists()
        assert path.name == "data_distribuidor"

    def test_resolve_known_file(self):
        path = resolve_data_path("pages/energia_por_distribuidor.py")
        assert path.exists()
