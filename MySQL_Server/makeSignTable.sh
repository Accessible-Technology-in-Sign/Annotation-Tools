#!/bin/bash

# Database credentials and details
DB_HOST="0.0.0.0"
DB_PORT="3306"
DB_NAME="annotationsDB"
DB_USER="root"
DB_PASS="tylerwashere"

# SQL command to create a table
SQL="CREATE TABLE IF NOT EXISTS sign_table (
    Sign VARCHAR(255) NOT NULL,
    Complete TINYINT(1) NOT NULL,
    PRIMARY KEY (Sign)
);"

# Execute the SQL command
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$SQL"

echo "Table created successfully."
