"""
LangChain SQL Agent for Demografy Insights Chatbot.

What this file does:
- Connects Gemini AI to the BigQuery database via LangChain
- LangChain acts as the "glue" between the AI and the database:
    1. User types a question
    2. LangChain sends the question + our few-shot examples to Gemini
    3. Gemini generates a SQL query
    4. LangChain runs that SQL against BigQuery
    5. LangChain sends the results back to Gemini to format a nice text answer
    6. The text answer is returned to the user

- LangSmith tracing happens automatically when LANGCHAIN_TRACING_V2=true in .env
  (you can see every step in the LangSmith dashboard)

HOW TO TEST (once BigQuery key is available):
    python -c "from agent.sql_agent import ask; print(ask('What are the top 3 suburbs in Victoria by diversity index?'))"
"""

import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.prompts import FEW_SHOT_PREFIX

# Load environment variables from .env file
load_dotenv()

# Module-level agent instance (created once, reused for all questions)
_agent = None


def _create_agent():
    """
    Creates the LangChain SQL agent.

    This is called once on first use. It:
    1. Connects to BigQuery using the service account credentials
    2. Creates a Gemini LLM instance
    3. Combines them into a SQL agent with our few-shot prompts

    Returns:
        A LangChain agent ready to answer questions.
    """
    # Step 1: Connect LangChain to BigQuery
    # SQLDatabase wraps BigQuery so LangChain can inspect the schema and run queries
    db = SQLDatabase.from_uri(
        "bigquery://demografy/prod_tables",
        include_tables=["a_master_view"],  # Only expose this table to the agent
        credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    )

    # Step 2: Create the Gemini LLM instance
    # temperature=0 means deterministic output (no randomness) — better for SQL
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite-preview-06-17",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )

    # Step 3: Create the SQL agent
    # The agent knows: the schema, our few-shot examples, and how to run SQL
    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",  # Tool-calling agent type (works with Gemini)
        prefix=FEW_SHOT_PREFIX,     # Our KPI mappings + example queries
        verbose=True,               # Print steps to terminal (good for debugging)
        max_iterations=10,          # Stop after 10 reasoning steps (prevents loops)
    )

    return agent


def ask(question: str) -> str:
    """
    Main function — takes a plain English question and returns a text answer.

    This is what the Streamlit app calls when a user submits a message.

    Args:
        question (str): The user's natural language question.
            e.g. "What are the top 3 suburbs in Victoria with the highest diversity?"

    Returns:
        str: A plain English answer with the data.
            e.g. "The top 3 most diverse suburbs in Victoria are:
                  1. Keilor Downs (0.95)
                  2. Delahey (0.94)
                  ..."

    Raises:
        Exception: If BigQuery connection fails or Gemini returns an error.
    """
    global _agent

    # Create the agent on first call, reuse on subsequent calls
    if _agent is None:
        _agent = _create_agent()

    # Run the agent — this triggers the full SQL generation + execution + formatting
    result = _agent.invoke({"input": question})

    # The agent returns a dict with an "output" key containing the text answer
    return result.get("output", "Sorry, I could not find an answer to your question.")
