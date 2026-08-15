import csv
from pathlib import Path
from app.db import get_connection, init_database

init_database()
conn=get_connection()
try:
    if __import__('app.config',fromlist=['get_settings']).get_settings().db_backend != 'sqlite':
        raise SystemExit('CSV bootstrap currently targets SQLite. Use DB_BACKEND=sqlite for local demo.')
    conn.execute('DELETE FROM store_week')
    rows=list(csv.DictReader(open(Path('data/store_week.csv'),newline='',encoding='utf-8')))
    conn.executemany('INSERT INTO store_week VALUES (?,?,?,?,?,?,?)',[(r['store_id'],r['week_start'],r['region'],float(r['sales']),int(r['orders']),float(r['promo_spend']),float(r['ads_spend'])) for r in rows])
    conn.commit()
    print(f'Loaded {len(rows)} rows into data/analytics.db')
finally:
    conn.close()
