from flask import Flask, render_template, request
import requests
import pandas as pd
import os
from env import API_KEY

app = Flask(__name__)

# Your SerpAPI key
SERPAPI_KEY = API_KEY

# Output Excel file
OUTPUT_FILE = "faculty_jobs.xlsx"

def fetch_jobs(keyword):
    results_seen = set()
    jobs = []

    for page in range(0, 1):  # 1 page (~10 results)
        start = page * 10
        url = f"https://serpapi.com/search.json?api_key={SERPAPI_KEY}&q={keyword}&start={start}"
        try:
            res = requests.get(url).json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs: {e}")
            return []

        for result in res.get("organic_results", []):
            link = result.get("link")
            if link and link not in results_seen:
                results_seen.add(link)
                jobs.append({
                    "Title": result.get("title", ""),
                    "Link": link
                })
    return jobs

def save_to_excel(jobs):
    new_df = pd.DataFrame(jobs)

    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_excel(OUTPUT_FILE)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["Title", "Link"], keep="last", inplace=True)
        except Exception as e:
            print(f"Error reading or processing Excel file: {e}")
            combined_df = new_df
    else:
        combined_df = new_df

    try:
        combined_df.to_excel(OUTPUT_FILE, index=False)
        print(f"✅ Jobs saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving to Excel file: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    show_no_results = False
    if request.method == 'POST':
        job_title = request.form['job_title']
        countries_input = request.form['countries']
        countries = [country.strip() for country in countries_input.split(',')]

        all_jobs = []
        for country in countries:
            keyword = f"{job_title} jobs in {country}"
            print(f"Searching for '{keyword}'...")
            country_jobs = fetch_jobs(keyword)
            if country_jobs:
                all_jobs.extend(country_jobs)
        
        if all_jobs:
            save_to_excel(all_jobs)
            jobs = all_jobs
        else:
            show_no_results = True

    return render_template('index.html', jobs=jobs, show_no_results=show_no_results)

if __name__ == '__main__':
    app.run(debug=True)
