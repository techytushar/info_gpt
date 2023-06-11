import json
import logging
import os
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from info_gpt import constants


def get_spaces(base_url, username, password, params=None, exclude=None):
    url = urljoin(base_url, "api/v2/spaces")
    response = requests.get(
        url,
        auth=(username, password),
        params=params,
        timeout=constants.READ_TIMEOUT,
    )
    if response.status_code != 200:
        error = (
            f"Failed to fetch list of spaces. {response.status_code} {response.text}"
        )
        raise Exception(error)

    spaces = json.loads(response.content)["results"]
    exclude = exclude or []
    return list(filter(lambda space: space["name"] not in exclude, spaces))


def get_pages_in_space(space_id, base_url, username, password, params=None):
    url = urljoin(base_url, f"api/v2/spaces/{space_id}/pages")
    params = params or {}
    next_token = True
    while next_token:
        response = requests.get(
            url,
            auth=(username, password),
            params=params,
            timeout=constants.READ_TIMEOUT,
        )
        if response.status_code != 200:
            error = (
                f"Failed to fetch list of pages in space {space_id}. {response.text}"
            )
            raise Exception(error)

        pages = json.loads(response.content)
        yield from pages["results"]

        next_token = None
        if pages.get("_links"):
            next_token = parse_qs(urlparse(pages["_links"]["next"]).query)["cursor"][0]
        params = {**params, "cursor": next_token}


def get_page_content(page_id, base_url, username, password, params=None):
    url = urljoin(base_url, f"rest/api/content/{page_id}")
    params = params or {}
    params = {
        **params,
        "expand": "body.storage",
    }
    response = requests.get(
        url,
        auth=(username, password),
        params=params,
        timeout=constants.READ_TIMEOUT,
    )
    if response.status_code != 200:
        error = f"Failed to fetch page content for page {page_id}. {response.text}"
        raise Exception(error)

    return json.loads(response.content)["body"]["storage"]["value"]


def read_all_pages():
    base_url = os.environ["CONFLUENCE_DOMAIN"]  # https://{org}.atlassian.net/wiki/
    username = os.environ["CONFLUENCE_USERNAME"]  # email
    password = os.environ[
        "CONFLUENCE_PASSWORD"
    ]  # https://id.atlassian.com/manage-profile/security/api-tokens

    spaces = get_spaces(
        base_url,
        username,
        password,
        {"type": "global", "limit": 100},
    )
    for space in spaces:
        logging.info(f"Fetching pages in space: {space['name']} ({space['id']})")
        pages = get_pages_in_space(
            space["id"],
            base_url,
            username,
            password,
            {"status": "current", "limit": 100, "body-format": "storage"},
        )
        result = []
        for page in pages:
            content = page["body"]["storage"]["value"]
            content = BeautifulSoup(content, "lxml").get_text(" ", strip=True)
            link = urljoin(base_url, page["_links"]["webui"][1:])
            result.append((content, link))
        logging.info(
            f"Found {len(result)} pages in space: {space['name']} ({space['id']})",
        )
        yield result
