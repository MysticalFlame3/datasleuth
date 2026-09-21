from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agent.state import AgentState
from agent.nodes import router_node, sql_generation_node, human_approval_node, sql_execution_node, support_rep_node, final_response_node

def route_intent(state: AgentState):
    if state.get("intent") == "policy_question":
        return "support_rep_node"
    return "sql_generation_node"

def should_interrupt(state: AgentState):
    if state.get("requires_approval") and not state.get("sql_result"):
        return "human_approval_node"
    return "sql_execution_node"

def handle_execution_result(state: AgentState):
    if state.get("sql_error"):
        return "sql_generation_node"
    return "final_response_node"

workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("sql_generation_node", sql_generation_node)
workflow.add_node("human_approval_node", human_approval_node)
workflow.add_node("sql_execution_node", sql_execution_node)
workflow.add_node("support_rep_node", support_rep_node)
workflow.add_node("final_response_node", final_response_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges("router", route_intent)
workflow.add_conditional_edges("sql_generation_node", should_interrupt)
workflow.add_edge("human_approval_node", "sql_execution_node")
workflow.add_conditional_edges("sql_execution_node", handle_execution_result)
workflow.add_edge("support_rep_node", END)
workflow.add_edge("final_response_node", END)

memory = MemorySaver()
# We interrupt BEFORE the human_approval_node so it pauses.
app = workflow.compile(checkpointer=memory, interrupt_before=["human_approval_node"])
