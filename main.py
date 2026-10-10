import argparse

import yaml

from database_sinks import TargetSinksManager   # fixed: module name, not file name


def load_job(path: str) -> dict:
    """Read a job definition (jobs/*.yaml) into the payload the sinks expect."""
    with open(path, encoding="utf-8") as f:
        job = yaml.safe_load(f)
    src, tgt = job["source"], job["target"]
    return {
        "name": job["name"],
        "stage": src["stage"],
        "filePattern": src["file_pattern"],
        "lakeUri": src["lake_uri"],
        "format": src["format"],
        "snowDatabase": tgt["database"],
        "snowSchema": tgt["schema"],
        "snowTable": tgt["table"],
        "columns": tgt["columns"],
    }


def run_generic_ingestion_pipeline(job_path: str) -> None:
    job = load_job(job_path)
    print(f"⚡ Starting metadata-driven pipeline '{job['name']}' ({job_path})...")
    sinks = TargetSinksManager()
    try:
        # Step A: load files from the stage into Snowflake
        full_target = f"{job['snowDatabase']}.{job['snowSchema']}.{job['snowTable']}"
        sinks.execute_snowflake_load(target_table=full_target, stage_name=job["stage"], file_pattern=job["filePattern"])

        # Step B: record lineage in the knowledge graph
        sinks.write_graph_lineage(job)
    except Exception as err:
        print(f"❌ Pipeline Ingestion Failure Encountered: {err}")
        raise
    finally:
        sinks.close()
        print("🏁 Sequence Terminated cleanly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run one ingestion job definition.")
    parser.add_argument("job", nargs="?", default="jobs/premium_whole_life.yaml", help="Path to a jobs/*.yaml file")
    run_generic_ingestion_pipeline(parser.parse_args().job)
