import psycopg2
from psycopg2 import sql
import json
from typing import Dict, Any

class PostgreSQLClient:
    def __init__(self, host, database, user, password, embedding_dimension):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.embedding_dimension = embedding_dimension
        self.connection = None

    def connect(self):
        """Establish a connection to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Database connection was successful")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def _validate_table_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate the table schema format."""
        required_keys = {'table_name', 'columns'}
        if not all(key in schema for key in required_keys):
            print(f"Schema must contain all required keys: {required_keys}")
            return False

        if not isinstance(schema['columns'], list):
            print("'columns' must be a list of column definitions")
            return False

        for column in schema['columns']:
            if not isinstance(column, dict) or 'name' not in column or 'type' not in column:
                print("Each column must have 'name' and 'type' defined")
                return False

        return True

    def _build_column_definition(self, column: Dict[str, Any]) -> sql.Composed:
        """Build SQL column definition from column schema."""
        parts = [sql.Identifier(column['name']), sql.SQL(column['type'])]

        if column.get('primary_key', False):
            parts.append(sql.SQL('PRIMARY KEY'))
        if column.get('not_null', False):
            parts.append(sql.SQL('NOT NULL'))
        if 'default' in column:
            parts.append(sql.SQL('DEFAULT {}').format(sql.Literal(column['default'])))

        return sql.SQL(' ').join(parts)

    def create_table_from_json(self, schema_json: str):
        """Create a table from JSON schema definition.
        
        Example schema format:
        {
            "table_name": "users",
            "columns": [
                {
                    "name": "id",
                    "type": "SERIAL",
                    "primary_key": true
                },
                {
                    "name": "username",
                    "type": "VARCHAR(255)",
                    "not_null": true
                },
                {
                    "name": "created_at",
                    "type": "TIMESTAMP",
                    "default": "CURRENT_TIMESTAMP"
                }
            ]
        }
        """
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return

        try:
            schema = json.loads(schema_json)
            if not self._validate_table_schema(schema):
                return

            cursor = self.connection.cursor()
            
            # Build column definitions
            column_definitions = [self._build_column_definition(col) for col in schema['columns']]
            
            # Create the CREATE TABLE query
            create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
                sql.Identifier(schema['table_name']),
                sql.SQL(', ').join(column_definitions)
            )

            cursor.execute(create_table_query)
            self.connection.commit()
            print(f"Table '{schema['table_name']}' created successfully")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            if cursor:
                cursor.close()

    def create_table(self):
        """Create the 'fc_table' with the specified columns and embedding dimension."""
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return

        try:
            cursor = self.connection.cursor()
            create_table_query = sql.SQL("""                CREATE TABLE IF NOT EXISTS fc_table (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    embedding VECTOR({dimension})
                );
            """).format(dimension=sql.Literal(self.embedding_dimension))

            cursor.execute(create_table_query)
            self.connection.commit()
            print("Table 'fc_table' created successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            if cursor:
                cursor.close()

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")

# Example usage
if __name__ == "__main__":
    from config import DB_CONFIG, TABLE_SCHEMA

    # Initialize the PostgreSQL client
    pg_client = PostgreSQLClient(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        embedding_dimension=DB_CONFIG["embedding_dimension"]
    )

    # Connect to the database
    pg_client.connect()

    # Create a table using the schema from config
    pg_client.create_table_from_json(TABLE_SCHEMA)

    # Close the database connection
    pg_client.close_connection()