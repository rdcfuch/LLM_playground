from typing import Optional, Dict, List
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

class TableConfig(BaseModel):
    """Table configuration settings"""
    name: str = Field(default=os.getenv('TABLE_NAME', 'documents'))
    columns: Dict[str, str] = Field(default_factory=lambda: json.loads(os.getenv('TABLE_COLUMNS', '{}')))
    primary_key: str = Field(default=os.getenv('TABLE_PRIMARY_KEY', 'id'))

class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    host: str = Field(default=os.getenv('DB_HOST', 'localhost'))
    port: int = Field(default=int(os.getenv('DB_PORT', '5432')))
    database: str = Field(default=os.getenv('DB_NAME', 'postgres'))
    user: str = Field(default=os.getenv('DB_USER', 'postgres'))
    password: str = Field(default=os.getenv('DB_PASSWORD', 'password'))
    embedding_dimension: int = Field(default=int(os.getenv('EMBEDDING_DIMENSION', '1536')))

class EmbeddingConfig(BaseModel):
    """Embedding service configuration settings"""
    service_type: str = Field(default=os.getenv('EMBEDDING_SERVICE_TYPE', 'openai'))
    openai_api_key: Optional[str] = Field(default=os.getenv('OPENAI_API_KEY'))
    openai_model: str = Field(default=os.getenv('OPENAI_MODEL', 'text-embedding-ada-002'))
    ollama_base_url: Optional[str] = Field(default=os.getenv('OLLAMA_BASE_URL'))
    ollama_model: str = Field(default=os.getenv('OLLAMA_MODEL', 'llama3.2:latest'))
    chunk_size: int = Field(default=int(os.getenv('CHUNK_SIZE', '500')))
    chunk_overlap: int = Field(default=int(os.getenv('CHUNK_OVERLAP', '50')))

class APIConfig(BaseModel):
    """API configuration settings"""
    api_key: Optional[str] = Field(default=os.getenv('API_KEY'))
    api_base_url: Optional[str] = Field(default=os.getenv('API_BASE_URL'))

class Config:
    """Main configuration class that combines all settings"""
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.table = TableConfig()
        self.embedding = EmbeddingConfig()

    def load_config(self):
        """Load and return a configuration instance"""
        return self

# Create a global config instance
config = Config().load_config()

# Export database configuration
DB_CONFIG = {
    'host': config.database.host,
    'database': config.database.database,
    'user': config.database.user,
    'password': config.database.password,
    'embedding_dimension': config.database.embedding_dimension
}

# Export table schema
TABLE_SCHEMA = json.dumps({
    'table_name': config.table.name,
    'columns': [
        {'name': name, 'type': type_info}
        for name, type_info in config.table.columns.items()
    ]
})

# Add primary key information
schema_dict = json.loads(TABLE_SCHEMA)
for column in schema_dict['columns']:
    if column['name'] == config.table.primary_key:
        column['primary_key'] = True
TABLE_SCHEMA = json.dumps(schema_dict)