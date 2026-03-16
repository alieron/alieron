import json
import yaml
import urllib.request
import os

with open("projects.yml") as f:
    config = yaml.safe_load(f)

username = config["username"]
categories = config["categories"]
allowlist = [repo for repos in categories.values() for repo in repos]

query = """
{
  viewer {
    repositories(first: 100, ownerAffiliations: OWNER) {
      nodes {
        name
        description
        url
        isPrivate
        primaryLanguage { name }
      }
    }
  }
}
"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query}).encode(),
    headers={
        "Authorization": f"bearer {os.environ['GH_TOKEN']}",
        "Content-Type": "application/json",
    },
)

with urllib.request.urlopen(req) as res:
    nodes = json.loads(res.read())["data"]["viewer"]["repositories"]["nodes"]

repo_map = {r["name"]: r for r in nodes if r["name"] in allowlist}

output = {"username": username, "categories": categories, "repos": repo_map}

with open("projects.json", "w") as f:
    json.dump(output, f, indent=2)
