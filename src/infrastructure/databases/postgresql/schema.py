from psycopg import sql


def drop_tables() -> sql.SQL:
    return sql.SQL("""
        DROP TABLE IF EXISTS product_file CASCADE;
        DROP TABLE IF EXISTS product CASCADE;
        DROP TABLE IF EXISTS accounts CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        DROP TABLE IF EXISTS spaces CASCADE;
    """)


def drop_types() -> sql.SQL:
    return sql.SQL("""
        DROP TYPE IF EXISTS role_type CASCADE;
        DROP TYPE IF EXISTS file_type CASCADE;
        DROP TYPE IF EXISTS product_status CASCADE;
        DROP TYPE IF EXISTS warranty_type CASCADE;
    """)


def create_role_type() -> sql.SQL:
    return sql.SQL("""
        CREATE TYPE role_type AS ENUM('admin', 'user');
    """)


def create_file_type() -> sql.SQL:
    return sql.SQL("""
        CREATE TYPE file_type AS ENUM('nf', 'photo', 'video', 'contract', 'other');
    """)


def create_product_status_type() -> sql.SQL:
    return sql.SQL("""
        CREATE TYPE product_status AS ENUM('active', 'inactive');
    """)


def create_warranty_type_enum() -> sql.SQL:
    return sql.SQL("""
        CREATE TYPE warranty_type AS ENUM('manufacturer', 'extended');
    """)


def create_spaces_table() -> sql.SQL:
    return sql.SQL("""
        CREATE TABLE IF NOT EXISTS spaces(
            id UUID PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(200) NOT NULL,
            utility_unit_number VARCHAR(50) NOT NULL,
            storage_quota BIGINT NOT NULL DEFAULT 1073741824,
            created_at TIMESTAMP NOT NULL
        );
    """)


def create_users_table() -> sql.SQL:
    return sql.SQL("""
        CREATE TABLE IF NOT EXISTS users(
            id UUID PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            role role_type NOT NULL DEFAULT 'user',
            is_approved BOOLEAN NOT NULL DEFAULT FALSE,
            storage_used BIGINT NOT NULL DEFAULT 0,
            space_id UUID REFERENCES spaces(id) ON DELETE CASCADE
        );
    """)


def create_accounts_table() -> sql.SQL:
    return sql.SQL("""
        CREATE TABLE IF NOT EXISTS accounts(
            id UUID PRIMARY KEY,
            email VARCHAR(320) UNIQUE NOT NULL,
            password VARCHAR(200) NOT NULL,
            created_at TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            reset_token VARCHAR(255),
            reset_token_expiry TIMESTAMP,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE
        );
    """)


def create_product_table() -> sql.SQL:
    return sql.SQL("""
        CREATE TABLE IF NOT EXISTS product(
            id UUID PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            category VARCHAR(50) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            location VARCHAR(100) NOT NULL,
            purchase_date DATE,
            purchase_value DECIMAL(10,2) NOT NULL,
            serial_number VARCHAR(100),
            warranty_type VARCHAR(20),
            warranty_expiry DATE,
            extended_warranty_expiry DATE,
            status product_status NOT NULL DEFAULT 'active',
            status_reason VARCHAR(50),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            space_id UUID REFERENCES spaces(id) ON DELETE CASCADE,
            created_at TIMESTAMP NOT NULL
        );
    """)


def create_product_file_table() -> sql.SQL:
    return sql.SQL("""
        CREATE TABLE IF NOT EXISTS product_file(
            id UUID PRIMARY KEY,
            file_path VARCHAR(500) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_type file_type NOT NULL,
            file_size BIGINT NOT NULL,
            uploaded_at TIMESTAMP NOT NULL,
            product_id UUID REFERENCES product(id) ON DELETE CASCADE,
            user_id UUID REFERENCES users(id) ON DELETE CASCADE
        );
    """)
