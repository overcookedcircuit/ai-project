import datetime
import json
import requests
from bs4 import BeautifulSoup

# prompt_template = ChatPromptTemplate.from_messages(
#     [
#         ("system",
#          "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. You always provide your sources when answering a question, providing the report name, link, and quoting the relevant information.{{reliefweb_data}}."),
#         ("user", "{{question}}"),
#     ]
# )


RELIEFWEB_API_URL = "https://api.reliefweb.int/v1"


def convert_to_iso8601(date_str):
    """
    Converts a date string to ISO 8601 format with timezone offset.

    Args:
        date_str (str): The date string to be converted.

    Returns:
        str: The converted date string in ISO 8601 format with timezone offset.

    Raises:
        None

    Examples:
        >>> convert_to_iso8601("2022-01-01")
        '2022-01-01T00:00:00+00:00'
    """
    try:
        # Parse the date string to a datetime object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        # Format the datetime object to ISO 8601 format with timezone offset
        iso8601_date = date_obj.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        return iso8601_date
    except ValueError:
        # Return the original string if it's not in the expected date format
        return date_str


def get_rweb_data(query: dict, endpoint: str) -> list:
    """
    Retrieves ReliefWeb data based on the provided query and endpoint.

    Args:
        query (dict): The query parameters for the ReliefWeb API.
        endpoint (str): The endpoint to retrieve data from.

    Returns:
        list: A list of report components containing relevant information from the retrieved data.
    """
    url = f"{RELIEFWEB_API_URL}/{endpoint}"

    # print(f"Getting {url} \n\n {query} ...")

    response = requests.post(url, json=query)
    if response.status_code == 200:
        answer = response.json()
    else:
        print("Error: No data was returned for keyword")
        query = str(query).replace("'", '"')
        return f"No data was returned for query: {query}"

    results = []
    for article in answer["data"]:
        article_url = article["fields"]["url"]
        article_response = requests.get(article_url)
        soup = BeautifulSoup(article_response.text, "html.parser")
        web_content = [p.text for p in soup.find_all("p")]
        article["fields"]["endpoint"] = endpoint
        article["fields"]["body"] = " ".join(web_content)  # Join paragraphs into a single string
        results.append(article["fields"])

    # print(f"REPORT SIZE {len(results)}")

    report_components = json.dumps(results, indent=4)

    return report_components


def get_rweb_reports_and_news_data(
        keyword: str = "",
        date_from: str = None,
        date_to: str = None,
        disaster_id: str = None,
        sort: str = None,
        limit: int = 1,
        offset: int = 0,
        format_name: str = None,
) -> list:
    """
    Retrieves reports and news data from ReliefWeb API based on the specified parameters.

    Args:
        keyword (str, optional): The keyword to search for in the reports and news data. Defaults to an empty string.
        date_from (str, optional): The starting date for the search in ISO 8601 format. Defaults to "2023-01-01T00:00:00+00:00".
        date_to (str, optional): The ending date for the search in ISO 8601 format. Defaults to "2025-01-01T00:00:00+00:00".
        disaster_id (str, optional): The ID of the disaster to filter the results. Defaults to None.
        sort (str, optional): The sorting order for the results. Defaults to "date.created:desc".
        limit (int, optional): The maximum number of results to retrieve. Defaults to 10.
        offset (int, optional): The offset for pagination. Defaults to 0.
        format_name (str, optional): The name of the format to filter the results. Defaults to None.

    Returns:
        str: The retrieved reports and news data in string format.
    """

    endpoint = "reports"
    filter = {"conditions": []}

    if date_from is not None and date_to is not None:
        date_from = convert_to_iso8601(date_from)
        date_to = convert_to_iso8601(date_to)
        filter_conditions = filter["conditions"]
        filter_conditions.append(
            {"field": "date.created", "value": {"from": date_from, "to": date_to}}
        )
        filter["conditions"] = filter_conditions

    if disaster_id is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "disaster.id", "value": disaster_id})
        filter["conditions"] = filter_conditions
    if format_name is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "format.name", "value": format_name})
        filter["conditions"] = filter_conditions
    limit = 1
    fields = {
        "include": [
            "title",
            "body",
            "url",
            "source",
            "date",
            "format",
            "status",
            "primary_country",
            "id",
        ]
    }
    query = {
        "appname": "myapp",
        "query": {"value": keyword, "operator": "AND"},
        "filter": filter,
        "limit": limit,
        "offset": offset,
        "fields": fields,
        "preset": "latest",
        "profile": "list",
    }
    if sort is not None:
        query["sort"] = [sort]

    # print(json.dumps(query, indent=4))

    return get_rweb_data(query, endpoint)


def get_rweb_disasters_data(
        keyword: str = "",
        date_from: str = None,
        date_to: str = None,
        sort: str = None,
        limit: int = 20,
        offset: int = 0,
        status: str = None,
        country: str = None,
        id: str = None,
        disaster_type: str = None,
        detailed_query: bool = False,
) -> list:
    """
    Retrieves disaster data from ReliefWeb API based on the specified parameters.

    Args:
        keyword (str, optional): Keyword to search for in the disaster data. Defaults to an empty string.
        date_from (str, optional): Start date for filtering the disaster data. Defaults to "2023-01-01T00:00:00+00:00".
        date_to (str, optional): End date for filtering the disaster data. Defaults to "2025-01-01T00:00:00+00:00".
        sort (str, optional): Sort order for the disaster data. Defaults to "date.event:desc".
        limit (int, optional): Maximum number of results to retrieve. Defaults to 20.
        offset (int, optional): Offset for pagination of results. Defaults to 0.
        status (str, optional): Filter by disaster status. Defaults to None.
        country (str, optional): Filter by country name. Defaults to None.
        id (str, optional): Filter by disaster ID. Defaults to None.
        disaster_type (str, optional): Filter by disaster type. Defaults to None.
        detailed_query (bool, optional): Flag indicating whether to include detailed description in the results. Defaults to False.

    Returns:
        str: JSON string containing the retrieved disaster data.
    """

    endpoint = "disasters"
    filter = {"operator": "AND", "conditions": []}
    if date_from is not None and date_to is not None:
        date_from = convert_to_iso8601(date_from)
        date_to = convert_to_iso8601(date_to)
        filter_conditions = filter["conditions"]
        filter_conditions.append(
            {"field": "date.event", "value": {"from": date_from, "to": date_to}}
        )
        filter["conditions"] = filter_conditions

    if status is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "status", "value": status})
        filter["conditions"] = filter_conditions
    if country is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "country.name", "value": country})
        filter["conditions"] = filter_conditions
    if disaster_type is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "type.name", "value": disaster_type})
        filter["conditions"] = filter_conditions
    if id is not None:
        filter_conditions = filter["conditions"]
        filter_conditions.append({"field": "id", "value": id})
        filter["conditions"] = filter_conditions

    fields = ["name", "date", "url", "id", "status", "glide", "country"]
    if detailed_query is True:
        fields.append("description")
    fields = {"include": fields}
    query = {
        "appname": "myapp",
        "query": {"value": keyword},
        "filter": filter,
        "limit": limit,
        "offset": offset,
        "fields": fields,
    }
    if sort is not None:
        query["sort"] = [sort]

    return get_rweb_data(query, endpoint)


class ReliefWebAPIWrapper:
    def run(self, user_input):
        return get_data(user_input)

# @tool
def get_data(query=None) -> str:
    """
    List or search updates, headlines, or maps.

    Args:
        query (str): The search query string.

    Returns:
        response containing reports, dictionary
    """

    # These are report format_name options as extracted from ReliefWeb API
    # [
    #    "Situation Report",
    #    "News and Press Release",
    #    "Assessment",
    #    "Appeal",
    #    "Policy Papers and Brief",
    #    "Map",
    #    "Infographic",
    #    "Bulletin",
    #    "Guideline",
    #    "Manuals and Handbook",
    #    "Evaluation",
    #    "Study",
    #    "Statistical Snapshot"
    # ],

    result = get_rweb_reports_and_news_data(
        keyword=query,
        date_from=None,
        date_to=None,
        sort=None,
        limit=5,
        offset=0,
        format_name="Situation Report",
    )

    # These are report disaster_type options as extracted from ReliefWeb API
    # [
    #     "Cold Wave",
    #     "Complex Emergency",
    #     "Drought",
    #     "Earthquake",
    #     "Epidemic",
    #     "Extratropical Cyclone",
    #     "Fire",
    #     "Flash Flood",
    #     "Flood",
    #     "Heat Wave",
    #     "Insect Infestation",
    #     "Land Slide",
    #     "Mud Slide",
    #     "Severe Local Storm",
    #     "Snow Avalanche",
    #     "Storm Surge",
    #     "Technological Disaster",
    #     "Tropical Cyclone",
    #     "Tsunami",
    #     "Volcano",
    #     "Wild Fire"
    # ],

    # result = get_rweb_disasters_data(query, limit=1)

    result = json.dumps(json.loads(result), indent=4)
    # print(result)

    return result


# if __name__ == "__main__":
# query = "sudan crises"
# result = get_rweb_reports_and_news_data(
#     keyword=query,
#     date_from=None,
#     date_to=None,
#     sort=None,
#     limit=5,
#     offset=0,
#     format_name="Situation Report",
# )
# result = json.loads(json.dumps(json.loads(result), indent=4))
# print("\n\n")
# for r in result:
#     print(r["title"])
#     print(r["primary_country"]["name"])
#     print("---------")
#     print(r["body"])
#     print()

query = "Snow avalanche total deaths every year?"


# tools = [get_data]
# os.environ["MISTRAL_API_KEY"] = getpass.getpass()
# llm = ChatMistralAI(model="mistral-large-latest")
# llm_with_tools = llm.bind_tools(tools)
# structured_llm = llm.with_structured_output(get_data(query))
# print(len(str(structured_llm)))
#
# # def example_chaining_prompt():
# #     prompt = ChatPromptTemplate.from_messages(
# #         [
# #             (
# #                 "system",
# #                 "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. You always provide your sources when answering a question, providing the report name, link, and quoting the relevant information.{{reliefweb_data}}.",
# #             ),
# #             ("user", "{{question}}"),
# #         ]
# #     )
# #     structured_output = llm.with_structured_output()
# #     chain = prompt_template | llm_with_tools
# #     response = chain.invoke(
# #         {
# #             "input_language": "English",
# #             "output_language": "Spanish",
# #             "input": "I love programming.",
# #         }
# #     )
#
# # _llm = llm.bind_tools([get_data], tool_choice="get_data")
#
# # Prompt 2
# # chain = prompt_template | llm_with_tools | StrOutputParser()
# # query = "Situation Report"
# # output = llm_with_tools.invoke(query).tool_calls

def convent_string_to_dictionary(data: str) -> dict:
    """
        Remove first and last character and convert to JSON.

        Args:
            data (str): The string to be converted to JSON.

        Returns:
            Converted data to dictionary
        """
    return json.loads(data[1:-1])


