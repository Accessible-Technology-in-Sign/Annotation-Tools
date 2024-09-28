#!/bin/bash

# Database credentials and details
DB_HOST="0.0.0.0"
DB_PORT="3306"
DB_NAME="annotationsDB"
DB_USER="root"
DB_PASS="tylerwashere"

# SQL command to create a table
SQL="CREATE TABLE IF NOT EXISTS Annotations (
    _id INT AUTO_INCREMENT PRIMARY KEY,
    Sign VARCHAR(255),
    User VARCHAR(255),
    DateTime DATETIME,
    good TINYINT(1),
    unrecognizable TINYINT(1),
    wrong_variant TINYINT(1),
    Other TINYINT(1),
    FOREIGN KEY (Sign) REFERENCES sign_table(Sign)
);"

# Execute the SQL command
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" -e "$SQL"

echo "Table created successfully."
