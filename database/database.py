"""
SQLite Database Layer for Enterprise GTM Account Intelligence Platform.
Saves, loads, renames, clones, and deletes company analysis runs (batches).
"""

import os
import sqlite3
import json
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Tuple

DEFAULT_DB_FILE = os.path.join(os.path.dirname(__file__), "gtm_intelligence.db")

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """Creates a database connection and enables dictionary-like row factory."""
    if db_path is None:
        db_path = DEFAULT_DB_FILE
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = None) -> None:
    """Initializes the database tables if they do not exist."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # 1. Companies Table
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
    
    # 2. Batches Metadata Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY,
            source_filename TEXT,
            record_count INTEGER,
            average_icp REAL,
            average_opp_score REAL,
            top_industry TEXT,
            top_region TEXT,
            top_tier TEXT,
            is_active INTEGER DEFAULT 1,
            quality_score INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Run migrations for existing databases
    try:
        cursor.execute("ALTER TABLE batches ADD COLUMN is_active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE batches ADD COLUMN quality_score INTEGER DEFAULT 100")
    except sqlite3.OperationalError:
        pass
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_batch_id ON companies(batch_id)")
    
    conn.commit()
    conn.close()


def save_company_batch(
    companies_list: List[Dict[str, Any]],
    batch_id: str,
    source_filename: str = "Unknown Source",
    quality_score: int = 100,
    db_path: str = None
) -> None:
    """
    Saves a batch of analyzed companies and automatically creates a metadata record in `batches`.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Calculate GTM statistics for the batches table
    record_count = len(companies_list)
    if record_count > 0:
        avg_icp = sum(float(c.get("icp_score", 0)) for c in companies_list) / record_count
        avg_opp = sum(float(c.get("gtm_opportunity_score", 0)) for c in companies_list) / record_count
        
        # Calculate modes
        industries = [c.get("Industry") for c in companies_list if c.get("Industry")]
        locations = [c.get("Location") for c in companies_list if c.get("Location")]
        tiers = [c.get("abm_tier") for c in companies_list if c.get("abm_tier")]
        
        top_ind = Counter(industries).most_common(1)[0][0] if industries else "Unknown"
        top_loc = Counter(locations).most_common(1)[0][0] if locations else "Unknown"
        top_tier = Counter(tiers).most_common(1)[0][0] if tiers else "Unknown"
    else:
        avg_icp, avg_opp = 0.0, 0.0
        top_ind, top_loc, top_tier = "None", "None", "None"
        
    # Save batch metadata
    cursor.execute("""
        INSERT OR REPLACE INTO batches (
            batch_id, source_filename, record_count, average_icp, average_opp_score, 
            top_industry, top_region, top_tier, is_active, quality_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, (batch_id, source_filename, record_count, avg_icp, avg_opp, top_ind, top_loc, top_tier, quality_score))
    
    # Insert company data
    query = """
        INSERT INTO companies (
            batch_id, company_name, industry, funding_stage, employee_count, location,
            hiring_activity, recent_funding, expansion_status, icp_score, abm_tier,
            buying_signal_score, buying_signal_level, market_opportunity_score,
            gtm_opportunity_score, gtm_opportunity_level, priority_level,
            outreach_reasoning, primary_contact, secondary_contact, contact_reasoning,
            account_summary, playbook, firmographic_segment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    records = []
    for c in companies_list:
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
    """Loads all company records for a given batch_id."""
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
        try:
            d["playbook"] = json.loads(d["playbook"])
        except (TypeError, json.JSONDecodeError):
            d["playbook"] = []
            
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


def list_batches(only_active: bool = False, db_path: str = None) -> List[Dict[str, Any]]:
    """Retrieves list of distinct batches from the metadata table."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM batches"
    if only_active:
        query += " WHERE is_active = 1"
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # If batches table is empty, do a fallback scan from companies table to populate it retroactively
    if not rows:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT batch_id FROM companies")
        legacy_batch_ids = [r["batch_id"] for r in cursor.fetchall()]
        conn.close()
        
        for lid in legacy_batch_ids:
            companies = load_companies_for_batch(lid, db_path=db_path)
            save_company_batch(companies, lid, source_filename="Legacy Ingestion", db_path=db_path)
            
        # Re-query
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        query = "SELECT * FROM batches"
        if only_active:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
    return [dict(r) for r in rows]


def delete_batch(batch_id: str, db_path: str = None) -> None:
    """Deletes all company records and batch metadata associated with a batch_id."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE batch_id = ?", (batch_id,))
    cursor.execute("DELETE FROM batches WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()


def rename_batch(old_id: str, new_name: str, db_path: str = None) -> str:
    """
    Renames a batch, generating a new suffix batch ID and updating both tables.
    """
    new_id = f"{new_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Update batches table
    cursor.execute("UPDATE batches SET batch_id = ?, source_filename = ? WHERE batch_id = ?", (new_id, new_name, old_id))
    # Update companies table
    cursor.execute("UPDATE companies SET batch_id = ? WHERE batch_id = ?", (new_id, old_id))
    
    conn.commit()
    conn.close()
    return new_id


def clone_batch(batch_id: str, clone_name: str, db_path: str = None) -> str:
    """
    Clones a batch by making copies of all records under a new batch ID.
    """
    companies = load_companies_for_batch(batch_id, db_path=db_path)
    new_id = f"{clone_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Get baseline quality score
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT quality_score FROM batches WHERE batch_id = ?", (batch_id,))
    row = cursor.fetchone()
    q_score = row["quality_score"] if row else 100
    conn.close()
    
    save_company_batch(
        companies_list=companies,
        batch_id=new_id,
        source_filename=clone_name,
        quality_score=q_score,
        db_path=db_path
    )
    return new_id


def set_batch_active_status(batch_id: str, is_active: int, db_path: str = None) -> None:
    """Updates the is_active status of a batch."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE batches SET is_active = ? WHERE batch_id = ?", (is_active, batch_id))
    conn.commit()
    conn.close()
