import pandas as pd
from utils.data_loader import build_date_mapping


def test_date_mapping_used_in_pages():
    mapping = build_date_mapping(2023, 2025)
    assert "012023" in mapping
    assert mapping["012023"] == "2023-01-01"
    assert "122025" in mapping
    assert mapping["122025"] == "2025-12-01"
    assert len(mapping) == 36


def test_date_mapping_single_month():
    mapping = build_date_mapping(2024, 2024)
    for m in range(1, 13):
        key = f"{m:02d}2024"
        assert key in mapping
        assert mapping[key] == f"2024-{m:02d}-01"
