from langchain.llms import OpenAI

from info_gpt import constants

openai_model = OpenAI(temperature=constants.TEMPERATURE)


def debug_logs(text: str):
    """Endpoint to debug logs.

    Parameters
    ----------
    text : str
        The logs to debug.

    Returns
    -------
    str
        The debugged logs.
    """
    text = (
        "Debug the following logs which were generated during building a Docker image: \n"
        + text
    )
    return openai_model(text)
