from src.Agent.Grapgh_state import AgentState
from langgraph.graph import END


#************ Routing after intent detection ************#
def route_intent(state: AgentState) -> str:
    """Route after intent check: go to SQL generation if relevant, else end."""
    
    return "generate_sql" if state.get('intent_result', '')== 'Yes' else END



#************ Routing after SQL execution ************#
def route_after_sql_result(state: AgentState) -> str:
    """Parse tool results and route accordingly.

    - On SUCCESS -> format_answer
    - On NO_DATA -> set query_result to 'no data found' and format_answer
    - On ERROR -> retry by returning 'generate_sql' while attempts < 10 else return 'sql_failed'
    """
    
    query_result = state.get('query_result', '')
    if (len(query_result) == 0) or (query_result is None) or (query_result.startswith("ERROR") == True):
        attempts = state.get('sql_attempts', 0)
        if attempts < 10:
            return "generate_sql"
        else:
            state['query_result'] = "sql failed"
            return "format_answer"
    else:
        # Successful result
        return "format_answer"
