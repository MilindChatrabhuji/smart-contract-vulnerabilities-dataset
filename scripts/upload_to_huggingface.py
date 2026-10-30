import argparse
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def upload_dataset(token=None, repo_id="MilindChatrabhuji/smart-contract-vulns-and-patches", dry_run=False):
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Error: huggingface_hub is not installed.")
        sys.exit(1)

    dataset_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(dataset_folder, "data")
    readme_path = os.path.join(dataset_folder, "README.md")

    if not os.path.exists(data_dir) or not os.path.exists(readme_path):
        print(f"Error: Dataset folder structure is invalid at {dataset_folder}")
        sys.exit(1)

    print(f"Dataset root: {dataset_folder}")
    print(f"Target Hugging Face Repo: {repo_id}")

    if dry_run:
        print("[DRY-RUN] Verified files ready for upload:")
        print(f"  • {readme_path}")
        for f in os.listdir(data_dir):
            print(f"  • {os.path.join(data_dir, f)}")
        print("[DRY-RUN] Success. Pass a valid Hugging Face token to upload live.")
        return True

    if not token:
        token = os.environ.get("HF_TOKEN")

    if not token:
        print("Error: No Hugging Face token provided.")
        print("Please provide --token <YOUR_HF_TOKEN> or set HF_TOKEN environment variable.")
        print("Get your free write token at: https://huggingface.co/settings/tokens")
        sys.exit(1)

    api = HfApi(token=token)
    print(f"Creating/verifying Hugging Face dataset repository: {repo_id}...")
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)

    print("Uploading dataset files to Hugging Face Hub...")
    # Upload README.md (Dataset Card)
    api.upload_file(
        path_or_fileobj=readme_path,
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="dataset"
    )

    # Upload data files
    for f in os.listdir(data_dir):
        full_path = os.path.join(data_dir, f)
        if os.path.isfile(full_path):
            print(f"Uploading {f}...")
            api.upload_file(
                path_or_fileobj=full_path,
                path_in_repo=f"data/{f}",
                repo_id=repo_id,
                repo_type="dataset"
            )

    hub_url = f"https://huggingface.co/datasets/{repo_id}"
    print(f"🎉 Dataset uploaded successfully! Live at: {hub_url}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset to Hugging Face Hub")
    parser.add_argument("--token", help="Hugging Face API Write Token (hf_...)")
    parser.add_argument("--repo-id", default="MilindChatrabhuji/smart-contract-vulns-and-patches", help="Target Hugging Face Dataset repo")
    parser.add_argument("--dry-run", action="store_true", help="Perform pre-flight verification without uploading")

    args = parser.parse_args()
    upload_dataset(token=args.token, repo_id=args.repo_id, dry_run=args.dry_run)
