import pandas as pd

from discovery.discover_greenhouse import discover_companies
from collectors.greenhouse_collector import collect_jobs
from core.job_filter import filter_jobs


def main():

    print("\nRADAR INICIADO\n")

    companies = discover_companies()

    print("Empresas descobertas:", len(companies))

    all_jobs = []

    for c in companies:

        df = collect_jobs(c)

        if df.empty:
            continue

        all_jobs.append(df)

        print("empresa com vagas:", c)

    if not all_jobs:

        print("Nenhuma vaga encontrada")
        return

    jobs = pd.concat(all_jobs, ignore_index=True)

    jobs = filter_jobs(jobs)

    jobs.to_csv("jobs.csv", index=False)

    print("\nVagas encontradas:", len(jobs))


if __name__ == "__main__":
    main()