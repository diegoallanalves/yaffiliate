import sqlite3
from pathlib import Path
import pandas as pd
DB_PATH=Path(__file__).resolve().parents[2]/"data"/"filtrify_ai.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def initialise_database():
    sql=["""CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,name TEXT NOT NULL,network TEXT,category TEXT,country TEXT,language TEXT,price REAL DEFAULT 0,commission REAL DEFAULT 0,commission_percent REAL DEFAULT 0,cpc REAL DEFAULT 0,search_volume INTEGER DEFAULT 0,competition REAL DEFAULT 0,refund_rate REAL DEFAULT 0,sales_page_url TEXT,affiliate_url TEXT,status TEXT DEFAULT 'Research',notes TEXT)""","""CREATE TABLE IF NOT EXISTS campaign_scenarios(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,product_name TEXT NOT NULL,budget REAL NOT NULL,cpc REAL NOT NULL,conversion_rate REAL NOT NULL,commission REAL NOT NULL,clicks REAL NOT NULL,sales REAL NOT NULL,revenue REAL NOT NULL,profit REAL NOT NULL,roas REAL NOT NULL,roi REAL NOT NULL,break_even_conversion_rate REAL NOT NULL)""","""CREATE TABLE IF NOT EXISTS keywords(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,keyword TEXT NOT NULL,intent TEXT,volume INTEGER DEFAULT 0,cpc REAL DEFAULT 0,competition REAL DEFAULT 0,product_name TEXT,status TEXT DEFAULT 'Idea')""","""CREATE TABLE IF NOT EXISTS settings(setting_key TEXT PRIMARY KEY,setting_value TEXT)"""]
    with get_connection() as c:
        for s in sql: c.execute(s)

def insert_record(table,values):
    if table not in {'products','campaign_scenarios','keywords'}: raise ValueError('Unsupported table')
    cols=', '.join(values); qs=', '.join('?' for _ in values)
    with get_connection() as c: c.execute(f'INSERT INTO {table} ({cols}) VALUES ({qs})',tuple(values.values()))

def read_table(table):
    if table not in {'products','campaign_scenarios','keywords','settings'}: raise ValueError('Unsupported table')
    with get_connection() as c: return pd.read_sql_query(f'SELECT * FROM {table} ORDER BY rowid DESC',c)

def delete_record(table,record_id):
    if table not in {'products','campaign_scenarios','keywords'}: raise ValueError('Unsupported table')
    with get_connection() as c: c.execute(f'DELETE FROM {table} WHERE id=?',(record_id,))

def upsert_setting(k,v):
    with get_connection() as c: c.execute('INSERT INTO settings(setting_key,setting_value) VALUES(?,?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value',(k,v))

def get_setting(k,default=''):
    with get_connection() as c: r=c.execute('SELECT setting_value FROM settings WHERE setting_key=?',(k,)).fetchone()
    return r['setting_value'] if r else default
