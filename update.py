import json
import yaml
import urllib.request
import os

with open("projects.yml") as f:
    config = yaml.safe_load(f)

username = config["username"]
categories = config["categories"]
allowlist = [repo for repos in categories.values() for repo in repos]

def parse_repo_ref(ref):
    if not isinstance(ref, str):
        raise TypeError(f"project entries must be strings, got {type(ref).__name__}")

    ref = ref.strip()
    github_prefix = "https://github.com/"

    if ref.startswith(github_prefix):
        path = ref[len(github_prefix):].strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] and parts[1]:
            return {"key": ref, "owner": parts[0], "name": parts[1], "external": True}

    if "/" in ref:
        owner, name = ref.split("/", 1)
        if owner and name:
            return {"key": ref, "owner": owner, "name": name, "external": True}

    return {"key": ref, "owner": username, "name": ref, "external": False}


def repo_payload(repo, display_name=None):
    return {
        "name": display_name or repo["name"],
        "description": repo.get("description"),
        "url": repo.get("url"),
        "isPrivate": repo.get("isPrivate"),
        "language": repo["primaryLanguage"]["name"] if repo.get("primaryLanguage") else None,
    }


repo_refs = [parse_repo_ref(repo) for repo in allowlist]
own_names = {repo["name"] for repo in repo_refs if not repo["external"]}
external_refs = [repo for repo in repo_refs if repo["external"]]

external_queries = "\n".join(
    f'  external{i}: repository(owner: {json.dumps(repo["owner"])}, name: {json.dumps(repo["name"])}) {{ ...RepoFields }}'
    for i, repo in enumerate(external_refs)
)

query = """
query {
  viewer {
    repositories(first: 100, ownerAffiliations: OWNER) {
      nodes {
        ...RepoFields
      }
    }
  }
__EXTERNAL_REPOS__
}

fragment RepoFields on Repository {
  name
  nameWithOwner
  description
  url
  isPrivate
  primaryLanguage { name }
}
""".replace("__EXTERNAL_REPOS__", external_queries)

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query}).encode(),
    headers={
        "Authorization": f"bearer {os.environ['GH_TOKEN']}",
        "Content-Type": "application/json",
    },
)

with urllib.request.urlopen(req) as res:
    data = json.loads(res.read())["data"]
    nodes = data["viewer"]["repositories"]["nodes"]

repo_map = {
    r["name"]: repo_payload(r)
    for r in nodes
    if r["name"] in own_names
}

for i, ref in enumerate(external_refs):
    repo = data.get(f"external{i}")
    if repo:
        repo_map[ref["key"]] = repo_payload(repo, repo["nameWithOwner"])

output = {"username": username, "categories": categories, "repos": repo_map}

os.makedirs("src/data", exist_ok=True)

with open("src/data/projects.json", "w") as f:
    json.dump(output, f, indent=2)
