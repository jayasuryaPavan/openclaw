import requests
import json

def search_all_jobs():
    url = "https://kinaxis.wd3.myworkdayjobs.com/wday/cxs/kinaxis/Kinaxis/jobs"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    # Let's search without a query to see all and filter for Java/Fullstack/React
    payload = {
        "appliedFacets": {},
        "limit": 50,
        "offset": 0,
        "searchText": ""
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for job in data.get("jobPostings", []):
                title = job.get('title', '')
                if any(k in title.lower() for k in ['java', 'full', 'stack', 'react', 'senior', 'software']):
                    print(f"Match: {title} | {job.get('locationsText')}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_all_jobs()
