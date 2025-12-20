
from typing import TypedDict, Annotated, List  
from typing_extensions import TypedDict  
from langchain_core.messages import BaseMessage
import operator

#********************** Agent State  **********************#
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    intent_result: str
    generated_sql: str
    sql_attempts: int  # Track retries (max 10)
    query_result: str
    final_answer: str