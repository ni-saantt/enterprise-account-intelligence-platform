"""
SQLite Database Layer for Enterprise GTM Account Intelligence Platform.
Saves, loads, and deletes company analysis runs (batches).
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

DEFAULT_DB_FILE = os.path.join(os.path.dirname(__file__), "gtm_intelligence.db")

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """Creates a database connection and enables dictionary-like row factory."""
    if db_path is None:
        db_path = DEFAULT_DB_FILE
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None) -> None:
    """Initializes the database tables if they do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Create companies table with complete GTM metrics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            industry TEXT,
            funding_stage TEXT,
            employee_count INTEGER,
            location TEXT,
            hiring_activity TEXT,
            recent_funding TEXT,
            expansion_status TEXT,
            icp_score INTEGER,
            abm_tier TEXT,
            buying_signal_score INTEGER,
            buying_signal_level TEXT,
            market_opportunity_score INTEGER,
            gtm_opportunity_score INTEGER,
            gtm_opportunity_level TEXT,
            priority_level TEXT,
            outreach_reasoning TEXT,
            primary_contact TEXT,
            secondary_contact TEXT,
            contact_reasoning TEXT,
            account_summary TEXT,
            playbook TEXT, -- JSON serialized list
            firmographic_segment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Index for fast batch lookup
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_id ON companies(batch_id)")
    
    conn.commit()
    conn.close()


def save_company_batch(
    companies_list: List[Dict[str, Any]],
    batch_id: str,
    db_path: str = None
) -> None:
    """
    Saves a batch of analyzed companies to the database.
    
    Args:
        companies_list: List of dictionaries containing all raw values and calculated scores.
        batch_id: Unique string identifying the upload batch.
        db_path: Optional path to SQLite file.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Insert batch data
    query = """
        INSERT INTO companies (
            batch_id, company_name, industry, funding_stage, employee_count, location,
            hiring_activity, recent_funding, expansion_status, icp_score, abm_tier,
            buying_signal_score, buying_signal_level, market_opportunity_score,
            gtm_opportunity_score, gtm_opportunity_level, priority_level,
            outreach_reasoning, primary_contact, secondary_contact, contact_reasoning,
            account_summary, playbook, firmographic_segment
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """
    
    records = []
    for c in companies_list:
        # Serialize playbook list to JSON string for SQLite storage
        playbook_json = json.dumps(c.get("playbook", []))
        
        records.append((
            batch_id,
            c.get("Company Name"),
            c.get("Industry"),
            c.get("Funding Stage"),
            int(c.get("Employee Count", 0)),
            c.get("Location"),
            c.get("Hiring Activity"),
            c.get("Recent Funding"),
            c.get("Expansion Status"),
            int(c.get("icp_score", 0)),
            c.get("abm_tier"),
            int(c.get("buying_signal_score", 0)),
            c.get("buying_signal_level"),
            int(c.get("market_opportunity_score", 0)),
            int(c.get("gtm_opportunity_score", 0)),
            c.get("gtm_opportunity_level"),
            c.get("priority_level"),
            c.get("outreach_reasoning"),
            c.get("primary_contact"),
            c.get("secondary_contact"),
            c.get("contact_reasoning"),
            c.get("account_summary"),
            playbook_json,
            c.get("firmographic_segment")
        ))
        
    cursor.executemany(query, records)
    conn.commit()
    conn.close()


def load_companies_for_batch(batch_id: str, db_path: str = None) -> List[Dict[str, Any]]:
    """Loads all company records for a given batch_id, converting Rows back to dicts."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM companies 
        WHERE batch_id = ? 
        ORDER BY gtm_opportunity_score DESC
    """, (batch_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        
        # De-serialize playbook back to Python list
        try:
            d["playbook"] = json.loads(d["playbook"])
        except (TypeError, json.JSONDecodeError):
            d["playbook"] = []
            
        # Re-map DB column names to what the frontend / core expect
        d["Company Name"] = d["company_name"]
        d["Employee Count"] = d["employee_count"]
        d["Funding Stage"] = d["funding_stage"]
        d["Hiring Activity"] = d["hiring_activity"]
        d["Recent Funding"] = d["recent_funding"]
        d["Expansion Status"] = d["expansion_status"]
        d["Location"] = d["location"]
        d["Industry"] = d["industry"]
        
        result.append(d)
        
    return result


def list_batches(db_path: str = None) -> List[Dict[str, Any]]:
    """Retrieves list of distinct batches, with upload timestamp and record counts."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            batch_id, 
            MIN(created_at) as created_at, 
            COUNT(id) as record_count 
        FROM companies 
        GROUP BY batch_id 
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]


def delete_batch(batch_id: str, db_path: str = None) -> None:
    """Deletes all company records associated with a batch_id."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()
