"""
CSV Validator and Value Normalizer for Ingestion 2.0.
Performs data quality checks, normalizes cell contents, and validates scoring boundaries.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any, List, Tuple
from utils.schema_registry import CANONICAL_COLUMNS, NORMALIZATION_MAPS

def normalize_cell_value(val: Any, canonical_column: str) -> Any:
    """
    Cleans and standardizes cell contents based on registry normalization maps.
    """
    if pd.isna(val) or val is None:
        if canonical_column == "Employee Count":
            return 0
        return "Unknown"
        
    # Standardize string values
    val_str = str(val).strip()
    
    if canonical_column == "Employee Count":
        try:
            # Strip non-numeric formatting (e.g. commas, pluses, spaces)
            num_str = re.sub(r'[^\d]', '', val_str)
            return int(num_str) if num_str else 0
        except (ValueError, TypeError):
            return 0
            
    # Apply category value cleaning
    if canonical_column in NORMALIZATION_MAPS:
        val_clean = val_str.lower()
        # Direct check
        if val_clean in NORMALIZATION_MAPS[canonical_column]:
            return NORMALIZATION_MAPS[canonical_column][val_clean]
        
        # Fuzzy strip space and check (e.g. 'seriesa' -> 'Series A')
        val_fuzz = re.sub(r'[^a-z0-9]', '', val_clean)
        for k, target in NORMALIZATION_MAPS[canonical_column].items():
            if re.sub(r'[^a-z0-9]', '', k) == val_fuzz:
                return target
                
    # Default capitalization for other strings
    return val_str.title() if len(val_str) > 2 else val_str.upper()


def audit_dataset_health(df_raw: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Analyzes raw DataFrame columns based on mappings to compile quality metrics.
    
    Returns:
        A dictionary containing:
            - total_records: int
            - duplicate_count: int
            - missing_counts: Dict[str, int]
            - quality_score: int (0-100)
            - warnings: List[str]
    """
    total_records = len(df_raw)
    if total_records == 0:
        return {
            "total_records": 0,
            "duplicate_count": 0,
            "missing_counts": {},
            "quality_score": 100,
            "warnings": []
        }
        
    missing_counts: Dict[str, int] = {canon: 0 for canon in CANONICAL_COLUMNS}
    warnings: List[str] = []
    
    # 1. Check for duplicates in Company Name
    raw_company_col = None
    for raw, canon in mapping.items():
        if canon == "Company Name":
            raw_company_col = raw
            break
            
    duplicate_count = 0
    if raw_company_col and raw_company_col in df_raw.columns:
        # Fuzzy duplicate detection: lowercase, strip spaces
        clean_companies = df_raw[raw_company_col].astype(str).str.lower().str.replace(r'[\s]+', '', regex=True)
        duplicate_count = int(clean_companies.duplicated().sum())
        if duplicate_count > 0:
            warnings.append(f"Detected {duplicate_count} duplicate company records.")
            
    # 2. Count missing values for each mapped required column
    total_missing_fields = 0
    for raw, canon in mapping.items():
        if canon in CANONICAL_COLUMNS and raw in df_raw.columns:
            nulls = df_raw[raw].isna().sum()
            empty_strings = (df_raw[raw].astype(str).str.strip() == "").sum()
            missing = int(nulls + empty_strings)
            missing_counts[canon] = missing
            total_missing_fields += missing
            if missing > 0:
                warnings.append(f"Missing {missing} values in '{canon}'.")
                
    # For columns not mapped at all, they count as 100% missing
    mapped_canonicals = set(mapping.values())
    for canon in CANONICAL_COLUMNS:
        if canon not in mapped_canonicals:
            missing_counts[canon] = total_records
            total_missing_fields += total_records
            warnings.append(f"Column '{canon}' is unmapped (counts as empty).")
            
    # 3. Calculate quality score
    # Score = 100 * (1 - TotalMissing / (Records * RequiredColumns)) - (Duplicates penalty)
    total_expected_cells = total_records * len(CANONICAL_COLUMNS)
    missing_ratio = total_missing_fields / total_expected_cells if total_expected_cells > 0 else 0
    duplicate_ratio = duplicate_count / total_records if total_records > 0 else 0
    
    quality_score = 100 * (1.0 - (0.8 * missing_ratio) - (0.2 * duplicate_ratio))
    quality_score = min(100, max(0, int(round(quality_score))))
    
    return {
        "total_records": total_records,
        "duplicate_count": duplicate_count,
        "missing_counts": missing_counts,
        "quality_score": quality_score,
        "warnings": warnings
    }


def validate_scoring_sanity(record: Dict[str, Any]) -> None:
    """
    Asserts that all scores and levels generated for a processed record fall within boundaries.
    Raises ValueError if corrupted numbers are found.
    """
    fields_to_check = {
        "icp_score": "ICP Fit Score",
        "buying_signal_score": "Buying Signal Score",
        "market_opportunity_score": "Market Opportunity Score",
        "gtm_opportunity_score": "GTM Opportunity Score"
    }
    
    for key, name in fields_to_check.items():
        val = record.get(key)
        if val is None or pd.isna(val):
            raise ValueError(f"Corrupted record: {name} is missing or NaN.")
            
        try:
            num = float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Corrupted record: {name} contains non-numeric value '{val}'.")
            
        if num < 0 or num > 100:
            raise ValueError(f"Corrupted record: {name} '{num}' is out of bounds (0-100).")
            
    # Validate Tiers
    tier = record.get("abm_tier")
    if tier not in ["Tier 1", "Tier 2", "Tier 3"]:
        raise ValueError(f"Corrupted record: Invalid ABM Tier '{tier}'.")
        
    # Validate Priorities
    priority = record.get("priority_level")
    if priority not in ["High", "Medium", "Low"]:
        raise ValueError(f"Corrupted record: Invalid priority level '{priority}'.")
