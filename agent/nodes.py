import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agent.state import AgentState
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model_name="qwen/qwen3.8-27b")

def router_node(state: AgentState):
    last_msg = state['messages'][-1].content
    prompt = f"""You are a router for DataSleuth. 
Given the user's query, classify it into one of two categories:
1. 'sql_analysis' - If the user is asking a data question that requires querying a database.
2. 'policy_question' - If the user is asking about company policies.

Respond with exactly one word: either 'sql_analysis' or 'policy_question'.

User Query: {last_msg}"""
    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()
    if 'policy' in intent:
        intent = 'policy_question'
    else:
        intent = 'sql_analysis'
    return {"intent": intent}

def sql_generation_node(state: AgentState):
    """Writes or fixes SQL."""
    from mcp_server.postgres_mcp import get_database_schema
    
    if state.get("sql_error"):
        prompt = f"""You are a Data Analyst. Your previous SQL query failed.
Query: {state['sql_query']}
Error: {state['sql_error']}
Write a corrected PostgreSQL query. Output ONLY the raw SQL query without explanations or markdown backticks."""
    else:
        schema = get_database_schema()
        prompt = f"""You are a Data Analyst. Write a PostgreSQL query to answer the user's question based on the schema.
Schema:
{schema}
User Question: {state['messages'][-1].content}

Output ONLY the SQL query, without any markdown formatting or explanations."""

    response = llm.invoke([HumanMessage(content=prompt)])
    sql = response.content.strip()
    if sql.startswith("```sql"): sql = sql[6:]
    if sql.endswith("```"): sql = sql[:-3]
    sql = sql.strip()
    
    # Check if dangerous
    is_dangerous = any(keyword in sql.upper() for keyword in ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER'])
    
    return {"sql_query": sql, "sql_error": None, "sql_result": None, "requires_approval": is_dangerous}

def human_approval_node(state: AgentState):
    """Dummy node that acts as a breakpoint. If we reach here, we are paused!"""
    return {}

def sql_execution_node(state: AgentState):
    """Executes the query."""
    from mcp_server.postgres_mcp import execute_sql
    
    result = execute_sql(state["sql_query"])
    if '{"error":' in result:
        return {"sql_error": result}
    else:
        return {"sql_result": result}

def support_rep_node(state: AgentState):
    from core.embeddings import embedding_service
    from mcp_server.postgres_mcp import get_connection
    
    last_msg = state['messages'][-1].content
    
    # Generate vector for the user's question
    question_vector = embedding_service.embed_text(last_msg)
    
    # Search Vector DB for the most relevant document
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content 
        FROM documents 
        ORDER BY embedding <=> %s::vector 
        LIMIT 1;
    """, (question_vector,))
    
    result = cursor.fetchone()
    context = result[0] if result else "No relevant policy found."
    
    cursor.close()
    conn.close()
    
    prompt = f"""You are a Support Representative. Answer the user's question using ONLY the provided context.
Context: {context}
User Question: {last_msg}"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [AIMessage(content=response.content)]}

def final_response_node(state: AgentState):
    if state.get("sql_result"):
        result_text = f"Here is the data you requested based on your query:\n\n{state['sql_result']}"
        return {"messages": [AIMessage(content=result_text)]}
    return {}
