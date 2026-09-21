from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain_core.messages import HumanMessage
from agent.graph import app as agent_app

app = FastAPI(
    title="DataSleuth AI API",
    description="Enterprise-grade Autonomous Data Analyst with HITL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ResumeRequest(BaseModel):
    approved: bool

# Hardcode a single thread_id for this demo
thread_config = {"configurable": {"thread_id": "1"}}

@app.get("/")
def read_root():
    return {"message": "Welcome to DataSleuth AI"}

def extract_response(final_state):
    intent = final_state.get("intent")
    sql_query = final_state.get("sql_query")
    sql_result = final_state.get("sql_result")
    
    response_msg = ""
    if final_state.get("messages"):
        for msg in reversed(final_state["messages"]):
            if msg.type == "ai":
                response_msg = msg.content
                break
                
    return {
        "intent": intent,
        "sql_query": sql_query,
        "response": response_msg,
        "sql_result": sql_result
    }

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=req.message)]
    }
    
    try:
        agent_app.invoke(initial_state, config=thread_config)
        
        # Check if we paused
        state_snapshot = agent_app.get_state(thread_config)
        
        if state_snapshot.next and state_snapshot.next[0] == "human_approval_node":
            # We are paused!
            return {
                "requires_approval": True,
                "sql_query": state_snapshot.values.get("sql_query")
            }
            
        return extract_response(state_snapshot.values)
    except Exception as e:
        return {"error": str(e)}

@app.post("/resume")
def resume_endpoint(req: ResumeRequest):
    try:
        if req.approved:
            # Resume the graph (it will enter human_approval_node and proceed to execute)
            agent_app.invoke(None, config=thread_config)
            state_snapshot = agent_app.get_state(thread_config)
            
            # Check if it paused AGAIN (e.g. it wrote a new dangerous query to fix an error)
            if state_snapshot.next and state_snapshot.next[0] == "human_approval_node":
                return {
                    "requires_approval": True,
                    "sql_query": state_snapshot.values.get("sql_query")
                }
                
            return extract_response(state_snapshot.values)
        else:
            # Cancel it
            return {
                "intent": "sql_analysis",
                "sql_query": None,
                "response": "Action rejected by user.",
                "sql_result": None
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
