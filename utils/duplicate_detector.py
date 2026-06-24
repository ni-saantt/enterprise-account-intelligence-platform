"""
Duplicate Detection and Resolution Engine for Ingestion 2.0.
Identifies fuzzy duplicates by company name and resolves them using First, Latest, or Merge logic.
"""

import pandas as pd
import re
from typing import Dict, Any, List

def clean_company_name_fuzz(name: str) -> str:
    """Standardizes company names for fuzzy duplicate detection (lowercase, removes spaces and dots)."""
    n = str(name).lower().strip()
    n = re.sub(r'[\s\-\.\,\&\/]+', '', n)
    return n


def resolve_duplicates(
    df: pd.DataFrame,
    company_column: str,
    strategy: str = "Keep First"
) -> pd.DataFrame:
    """
    Deduplicates a raw DataFrame by company name using the selected strategy.
    
    Strategies:
        - "Keep First": Retains the first record encountered.
        - "Keep Latest": Retains the last record encountered.
        - "Merge Records": Combines duplicates by taking maximum size and non-empty categories.
    """
    if df.empty or company_column not in df.columns:
        return df
        
    # Add a temporary helper column for grouping
    df_temp = df.copy()
    df_temp["_clean_company_fuzz"] = df_temp[company_column].apply(clean_company_name_fuzz)
    
    if strategy == "Keep First":
        df_clean = df_temp.drop_duplicates(subset=["_clean_company_fuzz"], keep="first")
    elif strategy == "Keep Latest":
        df_clean = df_temp.drop_duplicates(subset=["_clean_company_fuzz"], keep="last")
    else:  # Merge Records
        # We group by the fuzzy name and merge
        merged_rows = []
        for fuzz, group in df_temp.groupby("_clean_company_fuzz"):
            if len(group) == 1:
                merged_rows.append(group.iloc[0].to_dict())
                continue
                
            # Create a merged dictionary starting with the first record's keys
            merged = group.iloc[0].to_dict()
            
            # Find the record with the maximum employee count or longest company name
            max_emp = 0
            best_name = merged[company_column]
            
            # Look at columns to merge logically
            for _, row in group.iterrows():
                # Prefer longer company name (e.g. "Razorpay Inc" over "Razorpay")
                if len(str(row[company_column])) > len(str(best_name)):
                    best_name = row[company_column]
                    
                # Look for employee count column (try fuzzy finding)
                for col in group.columns:
                    if "employee" in col.lower() or "headcount" in col.lower() or "size" in col.lower():
                        try:
                            val = int(re.sub(r'[^\d]', '', str(row[col])))
                            if val > max_emp:
                                max_emp = val
                                merged[col] = row[col]
                        except Exception:
                            pass
                            
                # For string columns, pick the first value that is not "Unknown" or empty
                for col in group.columns:
                    if col in [company_column, "_clean_company_fuzz"]:
                        continue
                    # If current value in merged is empty/unknown, overwrite with this row's value if it's better
                    curr_val = str(merged[col]).strip().lower()
                    row_val = str(row[col]).strip()
                    row_val_lower = row_val.lower()
                    if curr_val in ["", "unknown", "nan", "none"] and row_val_lower not in ["", "unknown", "nan", "none"]:
                        merged[col] = row_val
                        
            merged[company_column] = best_name
            merged_rows.append(merged)
            
        df_clean = pd.DataFrame(merged_rows)
        
    # Drop the temporary fuzzy column
    if "_clean_company_fuzz" in df_clean.columns:
        df_clean = df_clean.drop(columns=["_clean_company_fuzz"])
        
    return df_clean
