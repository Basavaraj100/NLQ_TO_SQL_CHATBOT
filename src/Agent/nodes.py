from src.Agent.Grapgh_state import AgentState
from langchain_core.messages import  HumanMessage, AIMessage
from src.Agent.llm_model import get_llm_model
from src.Agent.structutred_output_schemas import IntentCheck,SQLQuery
from src.utils.basic_utils import load_yaml_config
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import ToolNode
from src.Agent.tools import execute_sql


# #************** Load DB Config **************#
db_config = load_yaml_config("configs/db_config.yaml")


#************************** Intent Check Nodes **************************#
def check_intent(state: AgentState) -> dict:
    """Node 1: Intent validation with structured output (defensive).

    Safely handle cases where `state['messages']` may be empty or not contain
    a message object with a `.content` attribute.
    """
    user_msg = state.get('user_query') or ''
    if len(user_msg.strip()) == 0:
        return {
            "messages": [HumanMessage(content=user_msg),
                         AIMessage(content="No user message found. Please ask a question.")],
            "intent_result": 'No'
        }

    else:
        
        
        system_prompt = """You are a SQL database assistant for STUDENT DOMAIN ONLY.

Available tables: students

VALID questions:
- Student: Student_id, First name, Last name, email/gmail, gpa, city , enrollment date of student
deeply analyse the question  and fast conversations and returh the intent of the question, if it is related to student domain return 'Yes' else 'No'
yield result in structured format as:
- is_relevant: bool
"""
        llm=get_llm_model()
        structured_llm = llm.with_structured_output(IntentCheck)
        result = structured_llm.invoke(system_prompt + f"\n\nQuery: {user_msg}"+f"\n past converastions: {state.get('messages',[])}")

        if not result.is_relevant:
            return {
                "messages": [HumanMessage(content=user_msg),
                             AIMessage(content=f"'{user_msg}' is not about student data. Please ask about students only." )],
                "intent_result": 'No'
            }

        return {"messages": [HumanMessage(content=user_msg),
                             AIMessage(content=f"'{user_msg}' is  about student data." )],
            "intent_result": 'Yes'}
    
    
    
    
    
#******************Generate SQL Node ******************#

def generate_sql_query(state: AgentState) -> dict:
    """Node 3: Generate SQL with schema context."""
    question = state['user_query']
    
    db= SQLDatabase.from_uri(db_config['db_path'])
    schema = db.get_table_info(["students"])

    system_prompt = """You are an expert SQL engineer. Generate SAFE SELECT queries ONLY.
    
Rules:
1. SELECT queries only - NO INSERT/UPDATE/DELETE
2. Use table schema provided
3. Handle edge cases (empty results, multiple tables)
4. High confidence queries only
5. Always limit the number of returned rows to 10 with "LIMIT 10" unless the question specifies otherwise.
    
Schema: {schema}
    
Question: {question}
    
Return structured SQL output as per the defined schema.

"""
    llm = get_llm_model()
    structured_llm = llm.with_structured_output(SQLQuery)
    result = structured_llm.invoke(system_prompt.format(schema=schema, question=question))

    # Provide an internal AIMessage containing the generated SQL so the ToolNode
    # can detect and execute it. The console runner filters messages that start
    # with "Generated SQL" in non-verbose mode.
    return {
        "generated_sql": result.sql_query,
        "sql_attempts": state.get('sql_attempts', 0) + 1,
        "messages": [AIMessage(content=f"Generated SQL \n{result.sql_query}")]
    }



#********************** Direct Execute SQL Node (wrapper) **********************#
def execute_sql_node(state: AgentState) -> dict:
    """Wrapper node that executes `generated_sql` directly via the execute_sql tool

    This avoids relying on ToolNode message-parsing. It sets `query_result` in
    the state and returns a short messages list for downstream routing.
    """
    sql = state.get('generated_sql') or ''
    if not sql:
        err = "ERROR: No SQL generated"
        return {"messages": [AIMessage(content=err)], "query_result": err}

    # Call the execute_sql tool function directly (it returns a status string)
    try:
        tool_out = execute_sql(sql)
    except Exception as e:
        err = f"ERROR: {e}"
        return {"messages": [AIMessage(content=err)], "query_result": err}

    # Parse tool output
    if isinstance(tool_out, str):
        if tool_out.startswith("SUCCESS:"):
            payload = tool_out.replace("SUCCESS:", "", 1).strip()
            return {"messages": [AIMessage(content=f"query result: {payload}")], "query_result": payload}

        if tool_out == "NO_DATA":
            return {"messages": [AIMessage(content="query result: NO_DATA")], "query_result": "no data found"}

        if tool_out.startswith("ERROR:"):
            return {"messages": [AIMessage(content=tool_out)], "query_result": tool_out}

    # Fallback: stringify whatever we got
    return {"messages": [AIMessage(content=str(tool_out))], "query_result": str(tool_out)}



#**************** Final answer format Node ******************#
def format_final_answer(state: AgentState) -> dict:
    """Node 5: Business-friendly answer (handles special outcomes)."""
    question = state.get('user_query', '')
    result = state.get('query_result', '')

    # Handle special terminal states
    if isinstance(result, str) and result.lower() == 'no data found':
        return {"messages": [AIMessage(content="No data found for your query.")],
                'final_answer': "No data found for your query."} 

    if isinstance(result, str) and result.lower() == 'sql failed':
        return {"messages": [AIMessage(content="SQL generation/execution failed after multiple attempts.")],
                'final_answer': "SQL generation/execution failed after multiple attempts."} 

    # Normal flow: convert raw SQL results to concise plain-text answer
    system_prompt = """
You are a helpful assistant. Based only on the provided Result, return a concise plain-text answer to the user's question.

- Do NOT include SQL, SQL keywords
- Do NOT hallucinate or make up data, only answer based on the Result provided.
- If Result indicates an error, apologize and state you could not retrieve data.
- If Result is a multi-row table, provide tables in markdown format and describe it.

Question: {question}
Result: {result}
"""

    llm = get_llm_model()
    response = llm.invoke(system_prompt.format(question=question,   result=result))

    final = response.content if hasattr(response, 'content') else str(response)
    final = final.strip()


    return {
        "messages": [AIMessage(content=final)],
        'final_answer': final
    }
