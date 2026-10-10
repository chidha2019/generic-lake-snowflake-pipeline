from database_sinks.py import TargetSinksManager

def run_generic_ingestion_pipeline():
    print("⚡ Starting Generic Data Lake to Snowflake Metadata-Driven Pipeline...")
    sinks = TargetSinksManager()

    # 1. Structural runtime payload configuration
    # In production, this can be dynamically constructed via file landing alerts (AWS S3 Event / Azure Event Grid)
    INGEST_JOB = {
        "lakeUri": "s3://massmutual-data-lake/premium-streams/2026/10/09/batch_99.parquet",
        "format": "Parquet",
        "snowDatabase": "MASSMUTUAL_EDW",
        "snowSchema": "RETAIL_INSURANCE",
        "snowTable": "SNOW_WHOLE_LIFE_LEDGER",
        "columns": [
            {"name": "POLICY_ID", "type": "VARCHAR(64)"},
            {"name": "PREMIUM_AMOUNT", "type": "NUMBER(18,2)"},
            {"name": "TRANSACTION_DATE", "type": "TIMESTAMP_NTZ"}
        ]
    }

    try:
        # Step A: Execute data loading inside your Snowflake storage layer
        full_target_string = f"{INGEST_JOB['snowDatabase']}.{INGEST_JOB['snowSchema']}.{INGEST_JOB['snowTable']}"
        sinks.execute_snowflake_load(
            target_table=full_target_string,
            stage_name="MASSMUTUAL_EDW.RETAIL_INSURANCE.MY_S3_STAGE",
            file_pattern=".*batch_99.parquet"
        )

        # Step B: Record the execution path inside your Knowledge Graph memory layer
        sinks.write_graph_lineage(INGEST_JOB)
        
    except Exception as err:
        print(f"❌ Pipeline Ingestion Failure Encountered: {str(err)}")
        
    finally:
        sinks.close()
        print("🏁 Sequence Terminated cleanly.")

if __name__ == "__main__":
    run_generic_ingestion_pipeline()
