import snowflake.connector
from neo4j import GraphDatabase
from config import PipelineConfig

class TargetSinksManager:
    def __init__(self):
        # Open parallel connections to both database layers
        self.sf_conn = snowflake.connector.connect(
            user=PipelineConfig.SNOW_USER,
            password=PipelineConfig.SNOW_PASSWORD,
            account=PipelineConfig.SNOW_ACCOUNT,
            warehouse=PipelineConfig.SNOW_WH,
            database=PipelineConfig.SNOW_DB,
            schema=PipelineConfig.SNOW_SCHEMA
        )
        self.neo4j_driver = GraphDatabase.driver(
            PipelineConfig.NEO4J_URI,
            auth=(PipelineConfig.NEO4J_USER, PipelineConfig.NEO4J_PASSWORD)
        )
        self._init_graph_constraints()

    def close(self):
        self.sf_conn.close()
        self.neo4j_driver.close()

    def _init_graph_constraints(self):
        """Enforces schema consistency rules across graph catalog markers."""
        with self.neo4j_driver.session() as session:
            session.run("CREATE CONSTRAINT lake_file IF NOT EXISTS FOR (l:DataLakeFile) REQUIRE l.uri IS UNIQUE;")
            session.run("CREATE CONSTRAINT snow_table IF NOT EXISTS FOR (t:SnowflakeTable) REQUIRE t.id IS UNIQUE;")

    def execute_snowflake_load(self, target_table, stage_name, file_pattern):
        """Triggers optimized COPY INTO commands inside the Snowflake cluster context."""
        query = f"""
            COPY INTO {target_table}
            FROM @{stage_name}
            FILE_FORMAT = (TYPE = 'PARQUET')
            PATTERN = '{file_pattern}'
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
        """
        with self.sf_conn.cursor() as cursor:
            cursor.execute(query)
            print(f"❄️ Snowflake execution complete: {cursor.rowcount} file structures cataloged.")

    def write_graph_lineage(self, tracking_payload):
        """Materializes physical data lake transit metadata directly inside Neo4j node structures."""
        cypher = """
            MERGE (l:DataLakeFile { uri: $lakeUri })
            ON CREATE SET l.format = $format, l.environment = 'Production'
            
            MERGE (t:SnowflakeTable { id: $snowDatabase + '.' + $snowSchema + '.' + $snowTable })
            ON CREATE SET t.name = $snowTable, t.schema = $snowSchema, t.database = $snowDatabase
            
            // Record the execution pipeline vector path
            MERGE (l)-[r:INGESTED_INTO { timestamp: timestamp(), status: 'COMPLETED' }]->(t)
            
            WITH t
            UNWIND $columns AS col
            MERGE (c:SnowflakeColumn { id: t.id + '.' + col.name })
            ON CREATE SET c.name = col.name, c.dataType = col.type
            MERGE (t)-[:HAS_COLUMN]->(c)
        """
        with self.neo4j_driver.session() as session:
            session.run(cypher, tracking_payload)
            print("⛓️ Lineage trace successfully synchronized into the semantic layer.")
