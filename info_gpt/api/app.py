"""API for receiving queries from user."""
from typing import Annotated

from fastapi import FastAPI, Form, HTTPException

from info_gpt.api import constants, tasks

from info_gpt.chat import ask, load_model

from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Info GPT",
    description="Information retrieval on your private data.",
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    query_text: str
   

@app.get("/")
async def health_check():
    return "OK"

@app.post("/query/")
async def answer_query(item: Item):
    answer = ask(item.query_text, load_model())
    return answer

@app.post("/slack/")
async def slack_query(
    token: Annotated[str, Form()],
    text: Annotated[str, Form()],
    response_url: Annotated[str, Form()],
):
    """Endpoint to receive slack queries using slack commands.
    Ref: https://api.slack.com/interactivity/slash-commands

    Parameters
    ----------
    token : str
        Slack slash command token to verify the request.
    text : str
        Query sent by the user.
    response_url : str
        Slack URL to send the final response to.

    Returns
    -------
    dict
        The response containing the query text and a processing message.

    Raises
    ------
    HTTPException
        401 exception is token is invalid.
    """
    if token != constants.SLACK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    tasks.get_answer_from_llm.delay(text, response_url)
    return {"text": f"*Query:* {text} \nProcessing your request..."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
