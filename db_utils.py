"""
Database connection utility for HSEFZ Digital Life project.

This module provides a centralized way to create database connections
using environment variables for configuration.
"""

import os
import mysql.connector
from dotenv import load_dotenv


def get_database_connection():
    """
    Create and return a MySQL database connection using environment variables.
    
    Environment variables used:
    - DB_HOST: Database host (default: localhost)
    - DB_PORT: Database port (default: 3306)
    - DB_USER: Database user (default: root)
    - DB_PASSWORD: Database password (required)
    - DB_NAME: Database name (default: selection_users)
    - DB_AUTH_PLUGIN: Authentication plugin (default: caching_sha2_password)
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
    
    Raises:
        mysql.connector.Error: If connection fails
    """
    # Load environment variables from .env file
    load_dotenv()
    
    connection_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'selection_users'),
        'auth_plugin': os.getenv('DB_AUTH_PLUGIN', 'caching_sha2_password')
    }
    
    # Remove None values to use defaults
    connection_config = {k: v for k, v in connection_config.items() if v is not None}
    
    return mysql.connector.connect(**connection_config)


def get_database_cursor():
    """
    Get a database connection and cursor.
    
    Returns:
        tuple: (connection, cursor) - Remember to close both when done
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    return connection, cursor


# Example usage:
if __name__ == "__main__":
    try:
        cnx, cursor = get_database_cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"Database connection test successful: {result}")
        cursor.close()
        cnx.close()
    except Exception as e:
        print(f"Database connection test failed: {e}")