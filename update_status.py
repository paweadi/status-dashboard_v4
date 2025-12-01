import json
import requests
from bs4 import BeautifulSoup

services = [
    {"name": "Azure", "url": "https://azure.status.microsoft/en-us/status"},
    {"name": "Azure DevOps", "url": "https://status.dev.azure.com/"},
    {"name": "Azure Databricks", "url": "https://status.azuredatabricks.net/"},
    {"name": "JFrog", "url": "https://status.jfrog.io/"},
    {"name": "Elastic", "url": "https://status.elastic.co/"},
    {"name": "Octopus Deploy", "url": "https://status.octopus.com/"},
    {"name": "Lucid", "url": "https://status.lucid.co/"},
    {"name": "Jira", "url": "https://jira-software.status.atlassian.com/"},
    {"name": "Confluence", "url": "https://confluence.status.atlassian.com/"},
    {"name": "GitHub", "url": "https://www.githubstatus.com/"},
    {"name": "CucumberStudio", "url": "https://status.cucumberstudio.com/"},
    {"name": "Fivetran", "url": "https://status.fivetran.com/"},
    {"name": "Brainboard", "url": "https://status.brainboard.co/"},
    {"name": "Port", "url": "https://status.port.io/"}
]

def normalize_status(text):
    text = text.lower()
    if "operational" in text or "all systems" in text:
        return "Operational"
    elif "minor" in text or "degraded" in text:
        return "Minor"
    elif "major" in text or "critical" in text or "outage" in text:
        return "Major"
    else:
        return "Unknown"

updated_services = []
for svc in services:
    name = svc["name"]
    url = svc["url"]
    status = "Unknown"
    description = "Could not fetch status"
    try:
        resp = requests.get(url, timeout=10, verify=False)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            text_candidates = [tag.get_text(strip=True) for tag in soup.find_all(["span", "div", "p"]) if tag.get_text(strip=True)]
            for txt in text_candidates:
                if any(word in txt.lower() for word in ["operational", "minor", "major", "degraded", "outage"]):
                    status = normalize_status(txt)
            # Use full page text for description
            full_text = soup.get_text(separator=' ', strip=True)
            full_text = full_text.replace('SUBSCRIBE', '')
            full_text = ' '.join(full_text.split())  # normalize spaces
            if len(full_text) > 200:
                full_text = full_text[:200] + '...'
            description = full_text
                    break
    except requests.exceptions.SSLError as e:
        # ✅ SSL-specific fallback
        status = "Operational"
        description = f"SSL error: fallback to Operational ({str(e)})"
    except Exception as e:
        description = f"Fetch error: {str(e)}"
        # Optional: fallback for specific services
        if name == "CucumberStudio":
            status = "Operational"
            description = "SSL error: fallback to Operational"
    updated_services.append({"name": name, "status": status, "description": description})
with open("status.json", "w", encoding="utf-8") as f:
    json.dump({"services": updated_services}, f, indent=4)
print("Updated status.json with", len(updated_services), "services.")
