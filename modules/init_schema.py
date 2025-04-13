import logging
import psycopg2
from connection_handler import ConnectionHandler

# Set up logging
logging.basicConfig(
    filename="logs/init_schema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("logs/init_schema.log")  # Log to file
    ]
)

# Log that schema creation is starting
logging.info("Starting schema creation process...")

# Initialize Connection Handler
handler = ConnectionHandler()

# Establish connection to the database
try:
    conn = handler.get_db_connection()
    logging.info("Database connection established.")
    
    # SQL script to create the full schema
    create_schema_sql = """
    
    
    -- Table: companies
    -- This table holds company-specific data.
    CREATE TABLE IF NOT EXISTS companies (
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
        company_address TEXT NOT NULL,
        gstin VARCHAR(15),
        currency_code VARCHAR(3),
        language_code VARCHAR(5),
        region_code VARCHAR(5),
        state_code VARCHAR(5)
    );

    -- Table: financial_years
    -- This table tracks the financial years for each company.
    CREATE TABLE IF NOT EXISTS financial_years (
        financial_year_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id) ON DELETE CASCADE,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        year_name VARCHAR(9) NOT NULL  -- E.g., "2024-2025"
    );

    -- Table: products
    -- This table holds product-specific data.
    CREATE TABLE IF NOT EXISTS products (
        product_id SERIAL PRIMARY KEY,
        product_code VARCHAR(50) NOT NULL UNIQUE,
        product_name VARCHAR(255) NOT NULL,
        description TEXT,
        unit VARCHAR(50),  -- Main unit (e.g., "pieces", "kg")
        alt_unit VARCHAR(50),  -- Alternate unit (e.g., "packet", "box")
        packaging_unit VARCHAR(50),  -- Packaging unit (e.g., "box", "carton")
        alt_packaging_unit VARCHAR(50),  -- Alternate packaging (e.g., "box2")
        price DECIMAL(10, 2) NOT NULL,  -- Default price
        manufacturer VARCHAR(255),
        barcode VARCHAR(255) UNIQUE,  -- Product barcode for easy billing
        manufacturing_date DATE,  -- Date of manufacturing
        expiry_date DATE,  -- Expiry date
        status VARCHAR(50) DEFAULT 'active',  -- Product status (e.g., "active", "inactive")
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Time when the product was created
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Time when the product was last updated
    );

    -- Table: product_aliases
    -- This table handles product aliases, allowing a product to have multiple names.
    CREATE TABLE IF NOT EXISTS product_aliases (
        alias_id SERIAL PRIMARY KEY,
        product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
        alias_name VARCHAR(255) NOT NULL
    );

    -- Table: customers
    -- This table holds customer-specific data.
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        customer_name VARCHAR(255) NOT NULL,
        customer_email VARCHAR(255),
        customer_phone VARCHAR(20),
        customer_address TEXT NOT NULL,
        gstin VARCHAR(15),
        language_code VARCHAR(5) DEFAULT 'en',  -- Default language for the customer
        region_code VARCHAR(5),
        state_code VARCHAR(5)
    );

    -- Table: orders
    -- This table tracks customer orders.
    CREATE TABLE IF NOT EXISTS orders (
        order_id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount DECIMAL(10, 2),
        total_tax DECIMAL(10, 2),
        total_before_tax DECIMAL(10, 2),
        invoice_number VARCHAR(100) UNIQUE,
        status VARCHAR(50) DEFAULT 'pending',  -- Order status
        language_code VARCHAR(5) DEFAULT 'en',  -- Language for billing
        financial_year_id INTEGER REFERENCES financial_years(financial_year_id)  -- Linking to financial year
    );

    -- Table: order_items
    -- This table tracks the individual items in an order.
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
        product_id INTEGER REFERENCES products(product_id),
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        discount DECIMAL(5, 2),
        scheme_applied BOOLEAN DEFAULT FALSE
    );

    -- Table: tax_rates
    -- This table defines tax rates, such as GST, VAT, etc., based on region.
    CREATE TABLE IF NOT EXISTS tax_rates (
        tax_rate_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id),
        region_code VARCHAR(5),
        tax_type VARCHAR(50) DEFAULT 'GST',  -- Type of tax (e.g., GST, VAT)
        tax_rate DECIMAL(5, 2),
        effective_from DATE,
        effective_to DATE
    );

    -- Table: schemes
    -- This table defines promotional schemes (discounts, free items, etc.).
    CREATE TABLE IF NOT EXISTS schemes (
        scheme_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id),
        scheme_name VARCHAR(255) NOT NULL,
        description TEXT,
        scheme_type VARCHAR(50),  -- 'Discount', 'Free Item', etc.
        start_date DATE,
        end_date DATE,
        min_quantity INTEGER,
        max_quantity INTEGER,
        scheme_rate DECIMAL(5, 2),
        free_item_product_id INTEGER REFERENCES products(product_id),
        applicable_on VARCHAR(50) DEFAULT 'quantity',  -- 'quantity' or 'amount'
        status VARCHAR(50) DEFAULT 'active'  -- Scheme status (active, expired)
    );

    -- Table: company_languages
    -- This table tracks the languages supported by each company for billing.
    CREATE TABLE IF NOT EXISTS company_languages (
        language_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id),
        language_code VARCHAR(5),
        language_name VARCHAR(255)
    );

    -- Table: company_addresses
    -- This table holds the address details for a company, including GSTIN.
    CREATE TABLE IF NOT EXISTS company_addresses (
        address_id SERIAL PRIMARY KEY,
        company_id INTEGER REFERENCES companies(company_id),
        address_line_1 TEXT NOT NULL,
        address_line_2 TEXT,
        city VARCHAR(100),
        state VARCHAR(100),
        country VARCHAR(100),
        postal_code VARCHAR(20),
        gstin VARCHAR(15),
        contact_number VARCHAR(20),
        is_primary BOOLEAN DEFAULT TRUE  -- Whether it's the primary address
    );

    -- Table: invoices
    -- This table holds the invoice information for orders.
    CREATE TABLE IF NOT EXISTS invoices (
        invoice_id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        invoice_number VARCHAR(100) UNIQUE,
        total_amount DECIMAL(10, 2),
        tax_amount DECIMAL(10, 2),
        net_amount DECIMAL(10, 2),
        paid_amount DECIMAL(10, 2) DEFAULT 0.00,
        status VARCHAR(50) DEFAULT 'unpaid'  -- Invoice status (e.g., 'paid', 'unpaid')
    );

    -- Table: payments
    -- This table tracks the payment information for orders.
    CREATE TABLE IF NOT EXISTS payments (
        payment_id SERIAL PRIMARY KEY,
        invoice_id INTEGER REFERENCES invoices(invoice_id),
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        amount DECIMAL(10, 2),
        payment_method VARCHAR(50),  -- Payment method (e.g., 'credit', 'debit', 'cash', etc.)
        transaction_id VARCHAR(100) UNIQUE
    );

    -- Table: shipping
    -- This table holds shipping information for orders.
    CREATE TABLE IF NOT EXISTS shipping (
        shipping_id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(order_id),
        shipping_address TEXT NOT NULL,
        shipping_method VARCHAR(100),
        tracking_number VARCHAR(100),
        shipping_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        delivery_date TIMESTAMP
    );
    """

    # Execute schema creation
    with conn.cursor() as cursor:
        cursor.execute(create_schema_sql)
        conn.commit()
        logging.info("Schema created successfully.")

except Exception as e:
    logging.error(f"Error occurred while creating the schema: {str(e)}")
finally:
    # Close connection
    if conn:
        conn.close()
        logging.info("Database connection closed.")
