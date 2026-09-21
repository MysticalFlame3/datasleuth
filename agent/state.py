import operator
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    intent: Optional[str]
    sql_query: Optional[str]
    sql_error: Optional[str]
    sql_result: Optional[str]
    requires_approval: Optional[bool]
