import os
from dotenv import load_dotenv

load_dotenv()

class PipelineConfig:
    # Snowflake Credentials
    SNOW_USER = os.getenv("SF_USER", "your_user")
    SNOW_PASSWORD = os.getenv("SF_PASSWORD", "your_password")
    SNOW_ACCOUNT = os.getenv("SF_ACCOUNT", "your_account_locator")
    SNOW_WH = os.getenv("SF_WAREHOUSE", "COMPUTE_WH")
    SNOW_DB = os.getenv("SF_DATABASE", "MASSMUTUAL_EDW")
    SNOW_SCHEMA = os.getenv("SF_SCHEMA", "PUBLIC")

    # Neo4j Graph Aura Credentials
    NEO4J_URI = os.getenv("NEO4J_AURA_URI", "neo4j+s://xxxxxxxx.databases.neo4j.io")
    NEO4J_USER = os.getenv("NEO4J_AURA_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_AURA_PASSWORD", "your_password")
