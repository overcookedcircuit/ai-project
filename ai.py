import api

# Set API key for Mistral
os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your Mistral API key: ")

# Instantiate the ChatMistralAI model
llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    # other params...
)


# First prompt
def first_prompt():
    messages = [
        (
            "system",
            "You are a helpful assistant. Using the output from a query to ReliefWeb, answer the user's question. You "
            "always provide your sources when answering a question, providing the report name, link, and quoting the "
            "relevant information.\n{reliefweb_data}.",
        ),
        ("user", "{question}"),
    ]
    ai_msg = llm.invoke(messages)
    print(ai_msg.content)


tools = [api.get_data]
