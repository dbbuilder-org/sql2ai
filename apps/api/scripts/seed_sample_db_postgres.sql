-- ============================================================================
-- SQL2.AI Sample Database Seed Script (PostgreSQL Version)
-- Creates sample tables and data for demonstration and testing
-- ============================================================================

-- ============================================================================
-- Create Tables
-- ============================================================================

-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_email CHECK (email ~ '^.+@.+\..+$')
);

-- Create indexes
CREATE INDEX ix_customers_email ON customers(email);
CREATE INDEX ix_customers_is_active ON customers(is_active);

-- Products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    unit_price DECIMAL(18,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 10,
    is_discontinued BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_price CHECK (unit_price >= 0),
    CONSTRAINT chk_stock CHECK (stock_quantity >= 0)
);

CREATE INDEX ix_products_category ON products(category);
CREATE INDEX ix_products_sku ON products(sku);

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    required_date TIMESTAMP WITH TIME ZONE,
    shipped_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    shipping_address VARCHAR(500),
    sub_total DECIMAL(18,2) NOT NULL DEFAULT 0,
    tax DECIMAL(18,2) NOT NULL DEFAULT 0,
    shipping_cost DECIMAL(18,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(18,2) GENERATED ALWAYS AS (sub_total + tax + shipping_cost) STORED,
    notes TEXT,
    CONSTRAINT chk_order_status CHECK (status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'))
);

CREATE INDEX ix_orders_customer_id ON orders(customer_id);
CREATE INDEX ix_orders_status ON orders(status);
CREATE INDEX ix_orders_order_date ON orders(order_date DESC);

-- Order Details table
CREATE TABLE order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(18,2) NOT NULL,
    discount DECIMAL(5,2) NOT NULL DEFAULT 0,
    line_total DECIMAL(18,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount)) STORED,
    CONSTRAINT chk_quantity CHECK (quantity > 0),
    CONSTRAINT chk_discount CHECK (discount >= 0 AND discount <= 1)
);

CREATE INDEX ix_order_details_order_id ON order_details(order_id);
CREATE INDEX ix_order_details_product_id ON order_details(product_id);

-- Employees table (for audit and DBA demos)
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    hire_date DATE NOT NULL,
    department VARCHAR(50),
    job_title VARCHAR(100),
    salary DECIMAL(18,2),
    ssn CHAR(11),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Audit Log table
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(128) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(128),
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX ix_audit_log_table_name ON audit_log(table_name, record_id);
CREATE INDEX ix_audit_log_changed_at ON audit_log(changed_at DESC);


-- ============================================================================
-- Create Views
-- ============================================================================

CREATE VIEW vw_customer_orders AS
SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    o.order_id,
    o.order_date,
    o.status,
    o.total_amount,
    COUNT(od.order_detail_id) AS item_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_details od ON o.order_id = od.order_id
GROUP BY
    c.customer_id, c.customer_name, c.email,
    o.order_id, o.order_date, o.status, o.total_amount;

CREATE VIEW vw_product_sales AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price AS current_price,
    COALESCE(SUM(od.quantity), 0) AS total_quantity_sold,
    COALESCE(SUM(od.line_total), 0) AS total_revenue,
    COUNT(DISTINCT od.order_id) AS number_of_orders
FROM products p
LEFT JOIN order_details od ON p.product_id = od.product_id
GROUP BY p.product_id, p.product_name, p.category, p.unit_price;

CREATE VIEW vw_monthly_revenue AS
SELECT
    EXTRACT(YEAR FROM order_date)::INTEGER AS year,
    EXTRACT(MONTH FROM order_date)::INTEGER AS month,
    COUNT(*) AS order_count,
    SUM(sub_total) AS sub_total,
    SUM(tax) AS tax_collected,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_order_value
FROM orders
WHERE status != 'Cancelled'
GROUP BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date);


-- ============================================================================
-- Create Functions and Procedures
-- ============================================================================

-- Get Customer Orders function
CREATE OR REPLACE FUNCTION fn_get_customer_orders(
    p_customer_id INTEGER,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    order_id INTEGER,
    order_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20),
    total_amount DECIMAL(18,2),
    product_id INTEGER,
    product_name VARCHAR(100),
    quantity INTEGER,
    unit_price DECIMAL(18,2),
    line_total DECIMAL(18,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.order_id,
        o.order_date,
        o.status,
        o.total_amount,
        od.product_id,
        p.product_name,
        od.quantity,
        od.unit_price,
        od.line_total
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    JOIN products p ON od.product_id = p.product_id
    WHERE o.customer_id = p_customer_id
        AND (p_start_date IS NULL OR o.order_date >= p_start_date)
        AND (p_end_date IS NULL OR o.order_date <= p_end_date)
    ORDER BY o.order_date DESC, od.order_detail_id;
END;
$$;

-- Create Order function
CREATE OR REPLACE FUNCTION fn_create_order(
    p_customer_id INTEGER,
    p_shipping_address VARCHAR(500) DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id INTEGER;
BEGIN
    -- Validate customer exists and is active
    IF NOT EXISTS (SELECT 1 FROM customers WHERE customer_id = p_customer_id AND is_active = TRUE) THEN
        RAISE EXCEPTION 'Customer not found or inactive';
    END IF;

    INSERT INTO orders (customer_id, shipping_address, status)
    VALUES (p_customer_id, p_shipping_address, 'Pending')
    RETURNING order_id INTO v_order_id;

    RETURN v_order_id;
END;
$$;

-- Add Order Item function
CREATE OR REPLACE FUNCTION fn_add_order_item(
    p_order_id INTEGER,
    p_product_id INTEGER,
    p_quantity INTEGER,
    p_discount DECIMAL(5,2) DEFAULT 0
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_unit_price DECIMAL(18,2);
    v_stock_quantity INTEGER;
BEGIN
    -- Get product info with lock
    SELECT unit_price, stock_quantity
    INTO v_unit_price, v_stock_quantity
    FROM products
    WHERE product_id = p_product_id
    FOR UPDATE;

    IF v_unit_price IS NULL THEN
        RAISE EXCEPTION 'Product not found';
    END IF;

    IF v_stock_quantity < p_quantity THEN
        RAISE EXCEPTION 'Insufficient stock';
    END IF;

    -- Add order detail
    INSERT INTO order_details (order_id, product_id, quantity, unit_price, discount)
    VALUES (p_order_id, p_product_id, p_quantity, v_unit_price, p_discount);

    -- Update stock
    UPDATE products
    SET stock_quantity = stock_quantity - p_quantity
    WHERE product_id = p_product_id;

    -- Update order subtotal
    UPDATE orders
    SET sub_total = (
        SELECT COALESCE(SUM(line_total), 0) FROM order_details WHERE order_id = p_order_id
    )
    WHERE order_id = p_order_id;
END;
$$;

-- Get Inventory Alerts function
CREATE OR REPLACE FUNCTION fn_get_inventory_alerts(
    p_threshold_percent INTEGER DEFAULT 20
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR(100),
    sku VARCHAR(50),
    category VARCHAR(50),
    stock_quantity INTEGER,
    reorder_level INTEGER,
    shortage_amount INTEGER,
    stock_status VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.product_id,
        p.product_name,
        p.sku,
        p.category,
        p.stock_quantity,
        p.reorder_level,
        (p.reorder_level - p.stock_quantity)::INTEGER AS shortage_amount,
        CASE
            WHEN p.stock_quantity = 0 THEN 'Out of Stock'::VARCHAR(20)
            WHEN p.stock_quantity < p.reorder_level THEN 'Low Stock'::VARCHAR(20)
            ELSE 'OK'::VARCHAR(20)
        END AS stock_status
    FROM products p
    WHERE p.stock_quantity <= p.reorder_level * (100 + p_threshold_percent) / 100
        AND p.is_discontinued = FALSE
    ORDER BY p.stock_quantity ASC;
END;
$$;


-- ============================================================================
-- Create Triggers (for audit demo)
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_customers_audit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, record_id, action, new_values, changed_by)
        VALUES ('customers', NEW.customer_id, 'INSERT', to_jsonb(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES ('customers', NEW.customer_id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, changed_by)
        VALUES ('customers', OLD.customer_id, 'DELETE', to_jsonb(OLD), current_user);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_customers_audit
AFTER INSERT OR UPDATE OR DELETE ON customers
FOR EACH ROW EXECUTE FUNCTION fn_customers_audit();


-- ============================================================================
-- Insert Sample Data
-- ============================================================================

-- Insert Customers
INSERT INTO customers (customer_name, email, phone, address, city, state, postal_code)
VALUES
    ('John Smith', 'john.smith@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001'),
    ('Jane Doe', 'jane.doe@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
    ('Bob Johnson', 'bob.j@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601'),
    ('Alice Brown', 'alice.b@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001'),
    ('Charlie Wilson', 'charlie.w@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001'),
    ('Diana Martinez', 'diana.m@email.com', '555-0106', '987 Cedar Ln', 'Philadelphia', 'PA', '19101'),
    ('Edward Lee', 'edward.l@email.com', '555-0107', '147 Birch Way', 'San Antonio', 'TX', '78201'),
    ('Fiona Garcia', 'fiona.g@email.com', '555-0108', '258 Spruce Ct', 'San Diego', 'CA', '92101'),
    ('George Taylor', 'george.t@email.com', '555-0109', '369 Walnut Blvd', 'Dallas', 'TX', '75201'),
    ('Hannah Anderson', 'hannah.a@email.com', '555-0110', '741 Cherry Ave', 'San Jose', 'CA', '95101');

-- Insert Products
INSERT INTO products (product_name, sku, category, description, unit_price, stock_quantity, reorder_level)
VALUES
    ('Laptop Pro 15', 'TECH-001', 'Electronics', 'High-performance laptop', 1299.99, 50, 10),
    ('Wireless Mouse', 'TECH-002', 'Electronics', 'Ergonomic wireless mouse', 29.99, 200, 30),
    ('USB-C Hub', 'TECH-003', 'Electronics', '7-port USB-C hub', 49.99, 150, 25),
    ('Office Chair', 'FURN-001', 'Furniture', 'Ergonomic office chair', 299.99, 30, 5),
    ('Standing Desk', 'FURN-002', 'Furniture', 'Adjustable standing desk', 499.99, 20, 5),
    ('Notebook Set', 'OFFC-001', 'Office Supplies', 'Pack of 5 notebooks', 12.99, 500, 100),
    ('Pen Pack', 'OFFC-002', 'Office Supplies', 'Pack of 10 pens', 8.99, 800, 150),
    ('Monitor 27"', 'TECH-004', 'Electronics', '27-inch 4K monitor', 349.99, 75, 15),
    ('Keyboard Mechanical', 'TECH-005', 'Electronics', 'Mechanical keyboard', 89.99, 100, 20),
    ('Webcam HD', 'TECH-006', 'Electronics', '1080p HD webcam', 79.99, 120, 25);

-- Insert Orders using the functions
DO $$
DECLARE
    v_order_id INTEGER;
BEGIN
    -- Order 1
    v_order_id := fn_create_order(1, '123 Main St, New York, NY 10001');
    PERFORM fn_add_order_item(v_order_id, 1, 1);
    PERFORM fn_add_order_item(v_order_id, 2, 2);
    UPDATE orders SET status = 'Delivered', shipped_date = NOW() - INTERVAL '5 days' WHERE order_id = v_order_id;

    -- Order 2
    v_order_id := fn_create_order(2);
    PERFORM fn_add_order_item(v_order_id, 4, 1);
    PERFORM fn_add_order_item(v_order_id, 5, 1);
    UPDATE orders SET status = 'Shipped', shipped_date = NOW() - INTERVAL '1 day' WHERE order_id = v_order_id;

    -- Order 3
    v_order_id := fn_create_order(3);
    PERFORM fn_add_order_item(v_order_id, 6, 10);
    PERFORM fn_add_order_item(v_order_id, 7, 5);
    UPDATE orders SET status = 'Processing' WHERE order_id = v_order_id;

    -- Order 4
    v_order_id := fn_create_order(1);
    PERFORM fn_add_order_item(v_order_id, 8, 2);
    UPDATE orders SET status = 'Pending' WHERE order_id = v_order_id;

    -- Order 5
    v_order_id := fn_create_order(4);
    PERFORM fn_add_order_item(v_order_id, 9, 1);
    PERFORM fn_add_order_item(v_order_id, 10, 1);
    PERFORM fn_add_order_item(v_order_id, 3, 2);
    UPDATE orders SET status = 'Delivered', shipped_date = NOW() - INTERVAL '10 days' WHERE order_id = v_order_id;
END $$;

-- Insert Employees (with sample PII for compliance testing)
INSERT INTO employees (first_name, last_name, email, phone, hire_date, department, job_title, salary, ssn)
VALUES
    ('Michael', 'Scott', 'michael.scott@company.com', '555-0201', '2010-03-15', 'Management', 'Regional Manager', 85000.00, '123-45-6789'),
    ('Jim', 'Halpert', 'jim.halpert@company.com', '555-0202', '2012-06-01', 'Sales', 'Sales Representative', 65000.00, '234-56-7890'),
    ('Pam', 'Beesly', 'pam.beesly@company.com', '555-0203', '2011-09-15', 'Administration', 'Office Administrator', 45000.00, '345-67-8901'),
    ('Dwight', 'Schrute', 'dwight.schrute@company.com', '555-0204', '2008-01-10', 'Sales', 'Assistant Regional Manager', 70000.00, '456-78-9012'),
    ('Angela', 'Martin', 'angela.martin@company.com', '555-0205', '2009-04-20', 'Accounting', 'Senior Accountant', 55000.00, '567-89-0123');

-- Success message
DO $$ BEGIN RAISE NOTICE 'Sample database seeded successfully!'; END $$;
