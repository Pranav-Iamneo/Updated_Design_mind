"""
LangGraph Workflow Graph Definition
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable

from state.models import HLDState
from .nodes import WorkflowNodes

def create_workflow_graph() -> Runnable:
    """Create the LangGraph workflow for HLD generation"""
    
    # Initialize nodes
    nodes = WorkflowNodes()
    node_runnables = nodes.get_node_runnables()
    
    # Create state graph
    workflow = StateGraph(Dict[str, Any])
    
    # Add nodes
    for node_name, node_runnable in node_runnables.items():
        workflow.add_node(node_name, node_runnable)
    
    # Set entry point
    workflow.set_entry_point("pdf_extraction")
    
    # Add edges - sequential flow with error handling
    workflow.add_edge("pdf_extraction", "auth_integrations")
    workflow.add_edge("auth_integrations", "domain_api_design") 
    workflow.add_edge("domain_api_design", "behavior_quality")
    workflow.add_edge("behavior_quality", "diagram_generation")
    workflow.add_edge("diagram_generation", "output_composition")
    workflow.add_edge("output_composition", END)
    
    # Compile the graph
    return workflow.compile()

def create_parallel_workflow_graph() -> Runnable:
    """Create a parallel workflow where some stages can run concurrently"""
    
    nodes = WorkflowNodes()
    node_runnables = nodes.get_node_runnables()
    
    workflow = StateGraph(Dict[str, Any])
    
    # Add nodes
    for node_name, node_runnable in node_runnables.items():
        workflow.add_node(node_name, node_runnable)
    
    # Add a coordination node for parallel execution
    def parallel_coordinator(state: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate parallel execution of auth, domain, and behavior analysis"""
        return state
    
    workflow.add_node("parallel_coordinator", parallel_coordinator)
    
    # Set entry point
    workflow.set_entry_point("pdf_extraction")
    
    # Sequential: PDF extraction first
    workflow.add_edge("pdf_extraction", "parallel_coordinator")
    
    # Parallel: Auth, Domain, and Behavior can run concurrently after PDF extraction
    workflow.add_edge("parallel_coordinator", "auth_integrations")
    workflow.add_edge("parallel_coordinator", "domain_api_design")
    workflow.add_edge("parallel_coordinator", "behavior_quality")
    
    # Sequential: Diagram generation after all analysis is complete
    workflow.add_edge("auth_integrations", "diagram_generation")
    workflow.add_edge("domain_api_design", "diagram_generation") 
    workflow.add_edge("behavior_quality", "diagram_generation")
    
    # Final: Output composition
    workflow.add_edge("diagram_generation", "output_composition")
    workflow.add_edge("output_composition", END)
    
    return workflow.compile()

def create_conditional_workflow_graph() -> Runnable:
    """Create a workflow with conditional routing based on state"""
    
    nodes = WorkflowNodes()
    node_runnables = nodes.get_node_runnables()
    
    workflow = StateGraph(Dict[str, Any])
    
    # Add nodes
    for node_name, node_runnable in node_runnables.items():
        workflow.add_node(node_name, node_runnable)
    
    # Add conditional router
    def route_next_step(state: Dict[str, Any]) -> str:
        """Route to next step based on current state"""
        return nodes.should_continue(state)
    
    workflow.add_node("router", route_next_step)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        route_next_step,
        {
            "pdf_extraction": "pdf_extraction",
            "auth_integrations": "auth_integrations",
            "domain_api_design": "domain_api_design", 
            "behavior_quality": "behavior_quality",
            "diagram_generation": "diagram_generation",
            "output_composition": "output_composition",
            "END": END
        }
    )
    
    # All nodes route back to router for next step determination
    for node_name in node_runnables.keys():
        workflow.add_edge(node_name, "router")
    
    return workflow.compile()