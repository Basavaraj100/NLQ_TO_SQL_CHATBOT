
from src.Agent.llm_model import get_llm_model
from src.Agent.workflow import get_workflow_graph
from langchain_core.messages import HumanMessage
from src.Agent.memory import get_memory
from src.utils.basic_utils import safe_set_env

import os
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv

load_dotenv()  # Load .env first
# Usage - Zero crashes
load_dotenv()
safe_set_env("OPENAI_API_KEY", "your-openai-key-here")
safe_set_env("LANGCHAIN_ENDPOINT", "")
safe_set_env("LANGCHAIN_API_KEY", "")
safe_set_env("LANGCHAIN_PROJECT", "default-project")
os.environ["LANGSMITH_TRACING"] = "true"

# print("🚀 Production env ready!")


def run_main(user_query, thread_id='main_thread_abc', verbose=False):
    #******** Get workflow graph ********#
    workflow= get_workflow_graph()
    checkpoint= get_memory()
    config = {"configurable": {"thread_id": thread_id}}

    
    #******** Compile it ********
    compiled_workflow = workflow.compile(checkpointer=checkpoint)

    #********** Initialize state with user question *********


    #********** Initialize state with user question *********
    initial_state = {
        "user_query": user_query
        }

    #********** Run the workflow **********
    
    final_state=compiled_workflow.invoke(initial_state, config=config)
    if final_state['intent_result']!='Yes':
        print("The question is not related to student data. Please ask about students only.")
        
    else:

        print(f' user question: {final_state["user_query"]}')
        print(f'Generated sql : {final_state["generated_sql"]}')
        print(f'Final answer: {final_state["final_answer"]}')

    
    return


if __name__ == "__main__":
    # user_query = "What are the names and GPA of students enrolled in the Computer Science course?"
    
    while True:
        user_query = input("Enter your query (or 'quit' to exit): ")
        if user_query.lower() in ('quit', 'exit','end'):
            break
        run_main(user_query,thread_id="main_thread_abc")
