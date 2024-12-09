import duckdb
import argparse
import pandas
import tabulate

# Verifying version
parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("--nightly_build")
args = parser.parse_args()

if not args:
    print("Usage: python scripts/count_consecutive_failures.py <input_file>.json --nightly_build <nightly-build>")

input_file = args.input_file
nightly_build = args.nightly_build

def count_consecutive_failures():
    result = duckdb.sql(f"""
        SELECT
            row_nr - 1
        FROM (
            SELECT
                row_number() over() AS row_nr,
                *
            FROM '{ input_file }'
            )
        WHERE conclusion = 'success'
        LIMIT 1
    """).fetchone()
    failures = result[0] if result else 'None'

    if failures > 0:
        failures_list = "failures_list.md"
        with open("nightly_failures_{}.md".format(nightly_build), 'w') as f:
            f.write(f"\n**{ nightly_build }** nightly-build has not succeeded the previous **{ failures }** times.\n")
            f.write(f"\n#### Failure Details\n")
            f.write(duckdb.query(f"""
                        SELECT
                            conclusion,
                            createdAt,
                            url
                        FROM '{ input_file }' 
                        WHERE conclusion = 'failure'
                        LIMIT '{ failures }'
                """).to_df().to_markdown(index=False)
            )
    else:
        with open("nightly_failures_{}.md".format(nightly_build), 'a') as f:
            f.write(f"\n**{ nightly_build }** nightly-build has succeeded.\n")
    url = duckdb.sql(f"SELECT url FROM '{ input_file }' LIMIT 1").fetchone()[0]
    with open("nightly_failures_{}.md".format(nightly_build), 'a') as f:
        f.write(f"\n\nSee the latest run: [ Run Link ]({ url })\n")

def main():
    count_consecutive_failures()
    
if __name__ == "__main__":
    main()