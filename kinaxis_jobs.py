import requests
import json

def search_jobs():
    url = "https://kinaxis.wd3.myworkdayjobs.com/wday/cxs/kinaxis/Kinaxis/jobs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": "Software"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data.get("jobPostings", []):
                print(f"Job: {job.get('title')}")
                print(f"Location: {job.get('locationsText')}")
                print(f"Posted: {job.get('postedOn')}")
                print("-" * 20)
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_jobs()
