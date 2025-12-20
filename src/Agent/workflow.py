

from langgraph.graph import END, StateGraph, START
from src.Agent.nodes import check_intent, generate_sql_query, execute_sql_node, format_final_answer
from src.Agent.routers import route_intent, route_after_sql_result
from src.Agent.Grapgh_state import AgentState



#****************** Define Workflow Graph ******************#
def get_workflow_graph() : 
    
    """Define the workflow graph for the agent."""
    workflow = StateGraph(AgentState)

        # Add nodes
    workflow.add_node("check_intent", check_intent)
    workflow.add_node("generate_sql", generate_sql_query)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("format_answer", format_final_answer)


    # Define edges
    workflow.add_edge(START, "check_intent")
    
    workflow.add_conditional_edges("check_intent", route_intent, {
    "generate_sql": "generate_sql",
    END: END})
    
    workflow.add_edge("generate_sql", "execute_sql")

    workflow.add_conditional_edges("execute_sql", route_after_sql_result, {
    "generate_sql": "generate_sql",    # Retry
    "format_answer": "format_answer",
    "sql_failed": "format_answer"})
    
    workflow.add_edge("format_answer", END)

    return workflow
    



