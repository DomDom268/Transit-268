from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL")
    
if DATABASE_URL is None:
    raise ValueError("DATABASE_PUBLIC_URL environment variable is not set.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL)


def migrate_csv_to_db(csv_file_path, table_name):
    df = pd.read_csv(csv_file_path)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

    return f"Data from {csv_file_path} has been migrated to the {table_name} table in the database."

tables = {
    "vehicles": "C:\\Users\\chris\\Downloads\\Tables\\vehicles.csv",
    "routes": "C:\\Users\\chris\\Downloads\\Tables\\routes.csv",
    "stops": "C:\\Users\\chris\\Downloads\\Tables\\stopNames.csv",
    "routes_stops": "C:\\Users\\chris\\Downloads\\Tables\\routes_stops.csv"
}

for table_name,csv_file in tables.items():
    print(migrate_csv_to_db(csv_file, table_name))


