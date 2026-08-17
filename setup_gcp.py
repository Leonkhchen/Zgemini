import subprocess
import json
import os
import sys

PROJECT_ID = "githubcodespace-505816"
SA_NAME = "cloudrun-deployer"
KEY_FILE = "gcp-key.json"
SA_EMAIL = f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com"

def run_cmd(cmd, check=True):
    print(f"--> Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and res.returncode != 0:
        print(f"Error ({res.returncode}): {res.stderr}")
        return None
    return res.stdout.strip()

print("=== [1/4] Setting GCP Project ===")
run_cmd(["gcloud", "config", "set", "project", PROJECT_ID])

print("=== [2/4] Enabling Required APIs ===")
run_cmd([
    "gcloud", "services", "enable",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com"
])

print("=== [3/4] Creating Service Account & IAM Roles ===")
sa_list = run_cmd(["gcloud", "iam", "service-accounts", "list", f"--filter=email:{SA_EMAIL}", "--format=value(email)"], check=False)
if not sa_list or SA_EMAIL not in sa_list:
    run_cmd(["gcloud", "iam", "service-accounts", "create", SA_NAME, "--display-name=Cloud Run Deployer"])
    print(f"Created Service Account: {SA_EMAIL}")
else:
    print(f"Service Account already exists: {SA_EMAIL}")

roles = [
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.admin",
    "roles/cloudbuild.builds.editor",
    "roles/storage.admin"
]

for role in roles:
    print(f"Binding role: {role} ...")
    run_cmd(["gcloud", "projects", "add-iam-policy-binding", PROJECT_ID, f"--member=serviceAccount:{SA_EMAIL}", f"--role={role}", "--quiet"])

print("=== [4/4] Generating JSON Key ===")
if os.path.exists(KEY_FILE):
    os.remove(KEY_FILE)

run_cmd(["gcloud", "iam", "service-accounts", "keys", "create", KEY_FILE, f"--iam-account={SA_EMAIL}"])

if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        key_data = f.read()
    print("\n" + "="*60)
    print("  GCP Setup & Key Generation Complete!")
    print("="*60)
    print(f"GCP_PROJECT_ID : {PROJECT_ID}")
    print(f"GCP_SA_KEY     :\n{key_data}")
    print("="*60)
else:
    print("Failed to generate key file.")
