from typing import Annotated

from fastapi import FastAPI, Form, HTTPException

from info_gpt.api import constants, tasks

app = FastAPI(
    title="Info GPT",
    description="Information retrieval on your private data.",
)


@app.get("/")
async def health_check():
    return "OK"


@app.post("/slack/")
async def slack_query(
    token: Annotated[str, Form()],
    text: Annotated[str, Form()],
    response_url: Annotated[str, Form()],
):
    if token != constants.SLACK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    tasks.send_top_k.delay(text, response_url)
    return {"text": "Processing your request..."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
