"""Constants required by the API"""
import os

SLACK_TOKEN = os.environ["SLACK_TOKEN"]

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
