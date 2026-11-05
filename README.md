# generic-lake-snowflake-pipeline

A metadata-driven ingestion pipeline: each job file in `jobs/` describes a Snowflake stage and a target table, and `main.py` loads the staged files into that table.

## Running locally

### Prerequisites

- Python and `pip`.
- A working Snowflake login that can use the warehouse, the stage and the target table in the job file.
- The project dependencies, installed from the repository root:

```bash
pip install -r requirements.txt
```

### Snowflake environment variables

`config.py` reads these variables. Replace the placeholders with your own values:

```bash
export SF_ACCOUNT="<account>"      # Snowflake account identifier (must be set: the code default is a placeholder)
export SF_USER="<user>"            # Snowflake login name (must be set: the code default is a placeholder)
export SF_PASSWORD="<password>"    # Password for that login (must be set: the code default is a placeholder)
export SF_WAREHOUSE="<warehouse>"  # Optional, defaults to COMPUTE_WH
export SF_DATABASE="<database>"    # Optional, the default is set in config.py
export SF_SCHEMA="<schema>"        # Optional, defaults to PUBLIC
```

You can also put these variables in a `.env` file at the repository root instead of exporting them. `config.py` loads that file automatically. Do not commit `.env`: it holds your credentials.

### Run the pipeline

From the repository root, run the default job (`jobs/premium_whole_life.yaml`):

```bash
python main.py
```

Or pass a job file explicitly:

```bash
python main.py jobs/premium_whole_life.yaml
```

The Snowflake stage and target table named in the job file must already exist, and the configured user must be able to reach them.
