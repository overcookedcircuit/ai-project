import os
import api
import getpass
from langchain.chains import LLMChain
from langchain_core.tools import Tool
from langchain_mistralai import ChatMistralAI
from langchain.prompts import ChatPromptTemplate

# Define the tool
tools = Tool(
    name="ReliefWebAPI",
    func=api.ReliefWebAPIWrapper.run,
    description="Queries the custom API with the user's query"
)

# Initialize the model with tools
os.environ["MISTRAL_API_KEY"] = getpass.getpass()
llm = ChatMistralAI(model="mistral-large-latest")
llm_with_tools = llm.bind_tools([tools])

# Define the prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",
         "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. "
         "You always provide your sources when answering a question. {relief_web_data}."),
        ("user", "{query}"),
    ]
)

# Fetch data using the tool
data = api.get_data(api.query)
schema = api.convent_string_to_dictionary(data)

# Format the prompt
query = "Snow avalanche total deaths every year?"
formatted_prompt = prompt_template.format_prompt(query=query, relief_web_data=schema)

# Invoke the model
response = llm_with_tools.invoke(input=formatted_prompt)
print(response.content)

# Process the response
if isinstance(response, dict):
    parsed_data = response.get("parsed")
    if parsed_data:
        answer = parsed_data.get("answer")
        justification = parsed_data.get("justification")
        print(f"Answer: {answer}")
        print(f"Justification: {justification}")

    raw_response = response.get("raw")
    if raw_response:
        raw_content = raw_response.get("content")
        print(f"Raw Response: {raw_content}")

    parsing_error = response.get("parsing_error")
    if parsing_error:
        print(f"Parsing Error: {parsing_error}")
