import requests
import pandas as pd
import os
from env import API_KEY

# Your SerpAPI key
SERPAPI_KEY = API_KEY

# Search keyword
KEYWORD = "computer science faculty jobs Gulf"

# Output Excel file
OUTPUT_FILE = "faculty_jobs.xlsx"

def fetch_jobs():
    results_seen = set()
    jobs = []

    for page in range(0, 10):  # 10 pages (~100 results)
        start = page * 10
        url = f"https://serpapi.com/search.json?api_key={SERPAPI_KEY}&q={KEYWORD}&start={start}"
        res = requests.get(url).json()

        for result in res.get("organic_results", []):
            link = result.get("link")
            if link and link not in results_seen:
                results_seen.add(link)
                jobs.append({
                    "Title": result.get("title", ""),
                    "Link": link
                })
                print(f"Saved job: {result.get('title', '')} - {link}")
    return jobs

def save_to_excel(jobs):
    new_df = pd.DataFrame(jobs)

    if os.path.exists(OUTPUT_FILE):
        # Append to existing file and drop duplicates
        existing_df = pd.read_excel(OUTPUT_FILE)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=["Title", "Link"], keep="last", inplace=True)
    else:
        combined_df = new_df

    combined_df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Jobs saved to {OUTPUT_FILE}")

def main():
    jobs = fetch_jobs()
    if jobs:
        save_to_excel(jobs)
    else:
        print("⚠ No jobs found.")

if __name__ == "__main__":
    main()
