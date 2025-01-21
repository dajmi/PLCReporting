import requests
import base64, re, os
from dotenv import load_dotenv

load_dotenv(override=True)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'dajmi'
REPO_NAME = 'PLCReporting'
COMMIT_MESSAGE = 'log upload'

def git_upload(FILE_NAME, FILE_PATH):
    # Read the file content and encode it in base64
    with open(FILE_PATH, 'rb') as file:
        content = base64.b64encode(file.read()).decode('utf-8')

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/logs/{FILE_NAME}'

    # print(GITHUB_TOKEN)
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
        payload = {
            'message': COMMIT_MESSAGE,
            'content': content,
            'sha': sha
        }
    else:
        payload = {
            'message': COMMIT_MESSAGE,
            'content': content
        }

    response = requests.put(url, json=payload, headers=headers)

    if response.status_code == 201 or response.status_code == 200:
        print('File uploaded successfully!')
        return True, f"https://github.com/{REPO_OWNER}/{REPO_NAME}/blob/main/logs/{FILE_NAME}"
    else:
        print(f'Failed to upload file: {response.status_code}')
        print(response.json())
        return False, "failed"


def summarize_log_to_markdown(log_filepath, log_filename, id):
    """
    Reads a log file, counts test successes and failures, and creates a 
    markdown summary with the counts and the full log content.

    Args:
        log_filepath: Path to the input log file.
        markdown_filepath: Path to the output markdown file.
	id: Test suite identifier.
    """
    md_filename = log_filename.replace(".log", ".md")
    md_filepath = f"local_logs/{md_filename}"
    id = id.replace('_', ' ')
    try:
        with open(log_filepath, 'r') as log_file:
            log_content = log_file.readlines()
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_filepath}")
        return

    success_count = 0
    failure_count = 0

    for line in log_content:
        if "TEST_CASE_SUCCESS" in line:
            success_count += 1
        elif "TEST_CASE_FAILURE" in line:
            failure_count += 1

    with open(md_filepath, 'w') as md_file:
        md_file.write(f"# Test Suite Summary: {id}\n\n")
        md_file.write(f"**Total Tests:** {success_count + failure_count}\n\n")
        md_file.write(f"**Total Successes:** {success_count}\n\n")
        md_file.write(f"**Total Failures:** {failure_count}\n\n")
        md_file.write("---\n\n")

        md_file.write("## Full Log Content\n\n")
        md_file.write("```\n")
        for line in log_content:
            md_file.write(line) 
        md_file.write("```\n")

    return md_filename, md_filepath
