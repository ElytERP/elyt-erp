import logging
from connection_handler import ConnectionHandler

# Set up logging
logging.basicConfig(
    filename="logs/flush_schema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("logs/flush_schema.log")  # Log to file
    ]
)

# Log that schema flushing is starting
logging.info("Starting schema flushing process...")

# Initialize Connection Handler
handler = ConnectionHandler()

# Establish connection to the database
try:
    conn = handler.get_db_connection()
    logging.info("Database connection established.")

    # SQL to drop tables and other objects (in order to avoid dependency errors)
    drop_all_sql = """
    -- Drop all views
    DO $$ 
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = 'public') LOOP
            EXECUTE 'DROP VIEW IF EXISTS public.' || r.table_name || ' CASCADE';
        END LOOP;
    END $$;
    
    -- Drop all sequences
    DO $$ 
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
            EXECUTE 'DROP SEQUENCE IF EXISTS public.' || r.sequence_name || ' CASCADE';
        END LOOP;
    END $$;

    -- Drop all indexes
    DO $$ 
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT indexname FROM pg_indexes WHERE schemaname = 'public') LOOP
            EXECUTE 'DROP INDEX IF EXISTS public.' || r.indexname || ' CASCADE';
        END LOOP;
    END $$;
    
    -- Drop all functions
    DO $$ 
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public') LOOP
            EXECUTE 'DROP FUNCTION IF EXISTS public.' || r.routine_name || ' CASCADE';
        END LOOP;
    END $$;

    -- Drop all triggers
    DO $$ 
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN (SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema = 'public') LOOP
            EXECUTE 'DROP TRIGGER IF EXISTS public.' || r.trigger_name || ' CASCADE';
        END LOOP;
    END $$;
    
    -- Drop all tables
    DROP TABLE IF EXISTS order_items CASCADE;
    DROP TABLE IF EXISTS invoices CASCADE;
    DROP TABLE IF EXISTS payments CASCADE;
    DROP TABLE IF EXISTS shipping CASCADE;
    DROP TABLE IF EXISTS tax_rates CASCADE;
    DROP TABLE IF EXISTS schemes CASCADE;
    DROP TABLE IF EXISTS company_addresses CASCADE;
    DROP TABLE IF EXISTS company_languages CASCADE;
    DROP TABLE IF EXISTS orders CASCADE;
    DROP TABLE IF EXISTS customers CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS product_aliases CASCADE;
    DROP TABLE IF EXISTS financial_years CASCADE;
    DROP TABLE IF EXISTS companies CASCADE;
    """

    # Execute flushing process
    with conn.cursor() as cursor:
        cursor.execute(drop_all_sql)
        conn.commit()
        logging.info("All tables, views, sequences, indexes, functions, and triggers flushed (dropped) successfully.")

except Exception as e:
    logging.error(f"Error occurred while flushing the schema: {str(e)}")
finally:
    # Close connection
    if conn:
        conn.close()
        logging.info("Database connection closed.")
