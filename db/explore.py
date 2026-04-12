"""
Data Exploration Script — Week 1 Tool

What this file does:
- Connects to BigQuery and runs basic queries to understand our data
- Run this ONCE after getting the service account key to document what's in the database
- Helps us write accurate few-shot prompts for the AI agent

HOW TO RUN (in terminal, with venv active):
    python db/explore.py
"""

from db.bigquery_client import run_query


def explore():
    print("=" * 60)
    print("Demografy — BigQuery Data Exploration")
    print("=" * 60)

    # 1. How many suburbs (SA2 areas) are there in total?
    print("\n[1] Total suburb count:")
    df = run_query("""
        SELECT COUNT(*) AS total_suburbs
        FROM demografy.prod_tables.a_master_view
    """)
    print(df.to_string(index=False))

    # 2. What are the unique state values? (Important for few-shot prompts)
    print("\n[2] Unique state values (exact spelling matters for SQL):")
    df = run_query("""
        SELECT DISTINCT state, COUNT(*) AS suburb_count
        FROM demografy.prod_tables.a_master_view
        GROUP BY state
        ORDER BY suburb_count DESC
    """)
    print(df.to_string(index=False))

    # 3. KPI ranges — min, max, average for each KPI
    print("\n[3] KPI value ranges:")
    df = run_query("""
        SELECT
            MIN(kpi_1_val) AS prosperity_min,  MAX(kpi_1_val) AS prosperity_max,
            MIN(kpi_2_val) AS diversity_min,   MAX(kpi_2_val) AS diversity_max,
            MIN(kpi_3_val) AS migration_min,   MAX(kpi_3_val) AS migration_max,
            MIN(kpi_4_val) AS learning_min,    MAX(kpi_4_val) AS learning_max,
            MIN(kpi_5_val) AS social_hsg_min,  MAX(kpi_5_val) AS social_hsg_max
        FROM demografy.prod_tables.a_master_view
    """)
    print(df.to_string(index=False))

    # 4. Check for nulls in key columns
    print("\n[4] Null counts in key columns:")
    df = run_query("""
        SELECT
            COUNTIF(sa2_name IS NULL)  AS null_sa2_name,
            COUNTIF(state IS NULL)     AS null_state,
            COUNTIF(kpi_1_val IS NULL) AS null_kpi_1,
            COUNTIF(kpi_2_val IS NULL) AS null_kpi_2,
            COUNTIF(kpi_3_val IS NULL) AS null_kpi_3
        FROM demografy.prod_tables.a_master_view
    """)
    print(df.to_string(index=False))

    # 5. Sample 5 rows to see what the data looks like
    print("\n[5] Sample 5 rows:")
    df = run_query("""
        SELECT sa2_name, state, kpi_1_val, kpi_2_val, kpi_3_val
        FROM demografy.prod_tables.a_master_view
        LIMIT 5
    """)
    print(df.to_string(index=False))

    # 6. Check dev_customers table
    print("\n[6] Customer table — sample rows:")
    df = run_query("""
        SELECT user_id, email, tier, is_active
        FROM demografy.ref_tables.dev_customers
        LIMIT 5
    """)
    print(df.to_string(index=False))

    print("\n" + "=" * 60)
    print("Exploration complete! Save these results for writing prompts.")
    print("=" * 60)


if __name__ == "__main__":
    explore()
