import json
import logging
import os

import requests
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI


class Agent:
    def __init__(self):
        self.llm = OpenAI(temperature=0)

    def workflow_agent(self, query):
        template = (
            "Extract the workflow name, number of steps and their image ids from the query at"  # noqa: ISC003
            + "the bottom and return as json format. If name is not present add a random word as workflow name.\n"
            + "Query: {question}"
        )
        prompt = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        answer = llm_chain.run(query)
        params = json.loads(answer)
        logging.info(params)
        steps = {
            f"step-{i}": {
                "type": "standard",
                "imageId": params["imageIds"][i],
                "command": "sample command",
            }
            for i in range(params["numberOfSteps"])
        }
        wf_body = {
            "name": params["workflowName"].lower(),
            "steps": steps,
        }
        logging.info(wf_body)
        response = requests.post(
            "https://service.dev.peak.ai/workflows/api/v1/workflows",
            json=wf_body,
            headers={
                "Authorization": os.environ["PEAK_API_KEY"],
            },
            timeout=10,
        )
        if response.status_code != 201:
            error = (
                f"Failed to create workflow {response.status_code}. {response.content}"
            )
            logging.error(error)
        return response
