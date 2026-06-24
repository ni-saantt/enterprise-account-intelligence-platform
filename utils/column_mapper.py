"""
Column Mapper for CSV Ingestion 2.0.
Maps raw CSV headers to canonical headers with fuzzy name matching.
"""

import re
from typing import List, Dict, Optional
from utils.schema_registry import CANONICAL_COLUMNS, COLUMN_ALIASES

def clean_header(header: str) -> str:
    """Standardizes header strings for comparison by lowercasing and removing symbols."""
    # Convert to string, lowercase, strip
    h = str(header).lower().strip()
    # Replace multiple spaces/underscores with a single space
    h = re.sub(r'[\s_\-]+', ' ', h)
    # Remove all non-alphanumeric/non-space characters
    h = re.sub(r'[^a-z0-9 ]', '', h)
    return h.strip()


def map_columns(raw_columns: List[str]) -> Dict[str, Optional[str]]:
    """
    Intelligently maps raw headers to canonical columns.
    
    Returns:
        A dict of {raw_header: mapped_canonical_name} (mapped_canonical_name is None if unmapped).
    """
    mapping: Dict[str, Optional[str]] = {}
    
    # Track which canonical columns have already been assigned to prevent double assignment
    assigned_canonical = set()
    
    for raw in raw_columns:
        cleaned_raw = clean_header(raw)
        matched_canonical = None
        
        # 1. Direct match check (cleaned raw vs cleaned canonical)
        for canon in CANONICAL_COLUMNS:
            if canon in assigned_canonical:
                continue
            if clean_header(canon) == cleaned_raw:
                matched_canonical = canon
                break
                
        # 2. Alias match check if direct match fails
        if not matched_canonical:
            for canon, aliases in COLUMN_ALIASES.items():
                if canon in assigned_canonical:
                    continue
                # Check if cleaned_raw matches any cleaned alias
                if any(clean_header(a) == cleaned_raw for a in aliases):
                    matched_canonical = canon
                    break
                    
        if matched_canonical:
            mapping[raw] = matched_canonical
            assigned_canonical.add(matched_canonical)
        else:
            mapping[raw] = None
            
    return mapping


def get_unmapped_required(mapping: Dict[str, Optional[str]]) -> List[str]:
    """Returns a list of canonical columns that were not mapped."""
    mapped_canonical = set(mapping.values())
    return [c for c in CANONICAL_COLUMNS if c not in mapped_canonical]
