"""
Automated Test Suite for CSV Ingestion 2.0.
Verifies column fuzzy mapping, value normalizations, deduplication strategies, and batch cloning.
"""

import sys
import os
import unittest
import pandas as pd
import sqlite3

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.column_mapper import map_columns, get_unmapped_required
from utils.csv_validator import normalize_cell_value, audit_dataset_health, validate_scoring_sanity
from utils.duplicate_detector import resolve_duplicates, clean_company_name_fuzz
from database.database import init_db, save_company_batch, load_companies_for_batch, rename_batch, clone_batch, list_batches

class TestIngestion2_0(unittest.TestCase):
    
    def setUp(self):
        # Temp database path for testing database operations
        self.test_db = os.path.join(os.path.dirname(__file__), "test_ingestion_temp.db")
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        init_db(self.test_db)
        
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def test_column_mapping_fuzzy(self):
        """Verifies that headers in different casings and aliases map to canonical columns."""
        headers = [
            "company_name",
            "industry_vertical",
            "fundinground",
            "headcount",
            "hq_location",
            "hiring status",
            "funding_recent",
            "growth status"
        ]
        
        mapping = map_columns(headers)
        
        # All columns should map correctly to their canonical equivalents
        self.assertEqual(mapping["company_name"], "Company Name")
        self.assertEqual(mapping["industry_vertical"], "Industry")
        self.assertEqual(mapping["fundinground"], "Funding Stage")
        self.assertEqual(mapping["headcount"], "Employee Count")
        self.assertEqual(mapping["hq_location"], "Location")
        self.assertEqual(mapping["hiring status"], "Hiring Activity")
        self.assertEqual(mapping["funding_recent"], "Recent Funding")
        self.assertEqual(mapping["growth status"], "Expansion Status")
        
        # Verify unmapped is empty
        unmapped = get_unmapped_required(mapping)
        self.assertEqual(len(unmapped), 0)
        
    def test_value_normalizations(self):
        """Verifies cell value cleans for funding, hiring, locations, and employees."""
        self.assertEqual(normalize_cell_value("series a", "Funding Stage"), "Series A")
        self.assertEqual(normalize_cell_value("SeriesA", "Funding Stage"), "Series A")
        self.assertEqual(normalize_cell_value("united states", "Location"), "US")
        self.assertEqual(normalize_cell_value("USA", "Location"), "US")
        self.assertEqual(normalize_cell_value("high", "Hiring Activity"), "High")
        self.assertEqual(normalize_cell_value("true", "Recent Funding"), "Yes")
        self.assertEqual(normalize_cell_value("expanding", "Expansion Status"), "Expanding")
        self.assertEqual(normalize_cell_value("5,000+", "Employee Count"), 5000)
        self.assertEqual(normalize_cell_value("N/A", "Employee Count"), 0)
        
    def test_duplicate_resolution(self):
        """Verifies duplicate resolution engines (Keep First, Keep Latest, Merge)."""
        data = [
            {"Company Name": "Razorpay", "Employee Count": 100, "Location": "India", "Industry": "FinTech"},
            {"Company Name": "RAZORPAY", "Employee Count": 200, "Location": "India", "Industry": "FinTech"},
            {"Company Name": "Razor Pay", "Employee Count": 150, "Location": "India", "Industry": "Unknown"}
        ]
        df = pd.DataFrame(data)
        
        # Fuzzy clean checks
        self.assertEqual(clean_company_name_fuzz("Razorpay"), "razorpay")
        self.assertEqual(clean_company_name_fuzz("Razor Pay"), "razorpay")
        self.assertEqual(clean_company_name_fuzz("RAZORPAY"), "razorpay")
        
        # 1. Keep First: should return row 0 (Razorpay, 100 emp)
        df_first = resolve_duplicates(df, "Company Name", "Keep First")
        self.assertEqual(len(df_first), 1)
        self.assertEqual(df_first.iloc[0]["Employee Count"], 100)
        self.assertEqual(df_first.iloc[0]["Company Name"], "Razorpay")
        
        # 2. Keep Latest: should return row 2 (Razor Pay, 150 emp)
        df_last = resolve_duplicates(df, "Company Name", "Keep Latest")
        self.assertEqual(len(df_last), 1)
        self.assertEqual(df_last.iloc[0]["Employee Count"], 150)
        self.assertEqual(df_last.iloc[0]["Company Name"], "Razor Pay")
        
        # 3. Merge: should merge to take max employee count (200) and pick better casing / non-empty values
        df_merge = resolve_duplicates(df, "Company Name", "Merge Records")
        self.assertEqual(len(df_merge), 1)
        self.assertEqual(df_merge.iloc[0]["Employee Count"], 200)
        # Location is retained
        self.assertEqual(df_merge.iloc[0]["Location"], "India")
        self.assertEqual(df_merge.iloc[0]["Industry"], "FinTech")
        
    def test_scoring_sanity_checks(self):
        """Checks validation layer rejects invalid, NaN, or out-of-range scoring data."""
        clean_record = {
            "icp_score": 80,
            "buying_signal_score": 70,
            "market_opportunity_score": 60,
            "gtm_opportunity_score": 75,
            "abm_tier": "Tier 2",
            "priority_level": "Medium"
        }
        
        # Should pass
        validate_scoring_sanity(clean_record)
        
        # Check out of range score
        bad_record1 = clean_record.copy()
        bad_record1["icp_score"] = 120
        with self.assertRaises(ValueError):
            validate_scoring_sanity(bad_record1)
            
        # Check NaN score
        bad_record2 = clean_record.copy()
        bad_record2["buying_signal_score"] = float("nan")
        with self.assertRaises(ValueError):
            validate_scoring_sanity(bad_record2)
            
        # Check negative score
        bad_record3 = clean_record.copy()
        bad_record3["market_opportunity_score"] = -5
        with self.assertRaises(ValueError):
            validate_scoring_sanity(bad_record3)
            
    def test_database_cloning_and_renaming(self):
        """Verifies cloning and renaming batches inside the database metadata tracker."""
        company_data = {
            "Company Name": "Clonable Inc",
            "Industry": "SaaS",
            "Funding Stage": "Seed",
            "Employee Count": 10,
            "Location": "US",
            "Hiring Activity": "Medium",
            "Recent Funding": "No",
            "Expansion Status": "Stable",
            "icp_score": 70,
            "abm_tier": "Tier 2",
            "buying_signal_score": 50,
            "buying_signal_level": "Medium",
            "market_opportunity_score": 65,
            "gtm_opportunity_score": 62,
            "gtm_opportunity_level": "Moderate Opportunity",
            "priority_level": "Medium",
            "outreach_reasoning": "Standard profile.",
            "primary_contact": "CEO",
            "secondary_contact": "VP Operations",
            "contact_reasoning": "Medium size.",
            "account_summary": "Summary details.",
            "playbook": ["1. Email"],
            "firmographic_segment": "SMB"
        }
        
        orig_batch = "orig_batch_id"
        save_company_batch([company_data], orig_batch, source_filename="original.csv", db_path=self.test_db)
        
        # Verify saved metadata
        batches = list_batches(db_path=self.test_db)
        self.assertEqual(len(batches), 1)
        self.assertEqual(batches[0]["source_filename"], "original.csv")
        
        # Rename batch
        new_batch_id = rename_batch(orig_batch, "renamed_batch", db_path=self.test_db)
        batches_renamed = list_batches(db_path=self.test_db)
        self.assertEqual(len(batches_renamed), 1)
        self.assertEqual(batches_renamed[0]["source_filename"], "renamed_batch")
        
        # Clone batch
        clone_id = clone_batch(new_batch_id, "cloned_batch", db_path=self.test_db)
        batches_all = list_batches(db_path=self.test_db)
        # Should have both renamed and cloned batches
        self.assertEqual(len(batches_all), 2)
        self.assertTrue(any(b["source_filename"] == "cloned_batch" for b in batches_all))
        self.assertTrue(any(b["source_filename"] == "renamed_batch" for b in batches_all))

if __name__ == "__main__":
    unittest.main()
