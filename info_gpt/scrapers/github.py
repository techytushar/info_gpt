"""Scrape data from files present in all repos inside and organization."""
import asyncio
import base64
import json
import logging
import os
import re

import aiohttp
import requests

from info_gpt import constants


def get_organization_repositories(org_name, token, page):
    url = f"https://api.github.com/orgs/{org_name}/repos?per_page=100&page={page}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers=headers, timeout=constants.READ_TIMEOUT)

    if response.status_code == 200:
        repositories = response.json()
        repository_names = [
            (repo["name"], repo["default_branch"])
            for repo in repositories
            if repo["archived"] is False
        ]
        return repository_names

    error = f"Failed to get list of repos in {org_name}. {response.text}"
    logging.error(error)
    return []


def _exclude_file(file_path):
    exclude_patterns = [
        ".github",
        "license.md",
        "contributing.md",
        "pull_request_template.md",
    ]
    pattern = rf"{'|'.join([re.escape(pat) for pat in exclude_patterns])}"
    return re.match(pattern, file_path, re.IGNORECASE) is not None


async def get_files(repo_owner, repo_name, branch, token, extension):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    logging.info(f"Getting {extension} files from {repo_owner}/{repo_name}")

    async with aiohttp.ClientSession(
        headers=headers,
        read_timeout=constants.READ_TIMEOUT,
    ) as session:
        async with session.get(url) as response:
            if response.status == 200:
                tree = await response.json()
                files = [
                    file
                    for file in tree["tree"]
                    if file["path"].endswith(extension)
                    and not _exclude_file(file["path"])
                ]
                logging.info(
                    f"Found {len(files)} {extension} files in {repo_owner}/{repo_name}",
                )
                return files

    error = f"Failed to get files list for {repo_owner}/{repo_name}. {response.status}"
    logging.error(error)
    return []


async def read_file(file_url, token):
    headers = {"Authorization": f"Bearer {token}"}

    async with aiohttp.ClientSession(
        headers=headers,
        read_timeout=constants.READ_TIMEOUT,
    ) as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                file_content = await response.text()
                return file_content

    error = f"Failed to read file at {file_url}. {response.text}"
    raise Exception(error)


async def read_all_files_in_org(org_name: str, extension: str):
    token = os.environ["GITHUB_TOKEN"]
    page = 1
    repos = get_organization_repositories(org_name, token, page)

    while repos:
        logging.info(f"{'-'*10}Got {len(repos)} repos on page {page}{'-'*10}")
        for repo, branch in repos:
            files = await get_files(org_name, repo, branch, token, extension)

            tasks = []
            for file in files:
                tasks.append(read_file(file["url"], token))

            file_contents = await asyncio.gather(*tasks)
            decoded_file_contents = []
            for content in file_contents:
                json_content = json.loads(content)
                decoded_file_contents.append(
                    {
                        "size": json_content["size"],
                        "url": json_content["url"],
                        "content": base64.b64decode(json_content["content"]),
                    },
                )
            if not decoded_file_contents:
                continue
            yield decoded_file_contents
        page += 1
        repos = get_organization_repositories(org_name, token, page)
