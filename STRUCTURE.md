# Project Structure - Graph and Nodes

## Directory Layout

```
DesignMind_GenAI_LangGraph/
├── graph.py                              # Main graph definition (ROOT LEVEL)
│
├── nodes/                                # Nodes folder (ROOT LEVEL)
│   ├── __init__.py                      # Package exports
│   ├── base_node.py                     # Abstract base class
│   ├── node_manager.py                  # Node manager
│   ├── pdf_extraction_node.py           # PDF extraction node
│   ├── auth_integrations_node.py        # Auth & integrations node
│   ├── domain_api_node.py               # Domain & API design node
│   ├── behavior_quality_node.py         # Behavior & quality node
│   ├── diagram_generation_node.py       # Diagram generation node
│   └── output_composition_node.py       # Output composition node
│
├── workflow/                             # Workflow orchestration
│   ├── __init__.py
│   ├── hld_workflow.py
│   └── parallel_safe.py
│
├── agent/                                # LLM agents
├── state/                                # State management
├── utils/                                # Utilities
└── ml/                                   # ML models
```

## Key Components

### Graph File (`graph.py`)
- **Location**: Root level
- **Purpose**: Define workflow graph structure and execution strategies
- **Main Class**: `WorkflowGraph`
  - `create_sequential_workflow_graph()`: Standard sequential execution
  - `create_parallel_workflow_graph()`: Optimized sequential execution
  - `create_conditional_workflow_graph()`: Conditional routing based on state
  - `create_graph(graph_type)`: Factory method
  - `get_execution_order()`: Get node sequence
  - `get_nodes_info()`: Get node information
  - `visualize()`: ASCII visualization of graph

### Nodes Folder (`nodes/`)
- **Location**: Root level (outside workflow)
- **Purpose**: Individual node implementations
- **Structure**:
  - `base_node.py`: Abstract base class for all nodes
  - `node_manager.py`: Central node management
  - Individual node files (one per node)

### BaseNode Class
```python
class BaseNode(ABC):
    def __init__(self, name, description, critical)
    @abstractmethod
    def execute_logic(hld_state) -> Any
    def execute(state) -> Dict[str, Any]
    def get_runnable() -> RunnableLambda
    def get_info() -> Dict[str, Any]
```

### Individual Nodes

1. **PDFExtractionNode** (Critical)
   - Extracts and parses PDF documents
   - Dependencies: None

2. **AuthIntegrationsNode**
   - Analyzes authentication mechanisms and integrations
   - Dependencies: pdf_extraction

3. **DomainAPINode**
   - Designs domain models and API interfaces
   - Dependencies: auth_integrations

4. **BehaviorQualityNode**
   - Analyzes behavior patterns and quality metrics
   - Dependencies: domain_api_design

5. **DiagramGenerationNode**
   - Generates visual diagrams and representations
   - Dependencies: behavior_quality

6. **OutputCompositionNode**
   - Composes and formats final output
   - Dependencies: diagram_generation

### NodeManager Class
Manages all workflow nodes:
- `get_node(name)`: Get a node by name
- `get_all_nodes()`: Get all nodes
- `get_node_runnables()`: Get RunnableLambda objects
- `get_nodes_info()`: Get node information
- `get_execution_order()`: Get execution sequence
- `get_node_dependencies(name)`: Get node dependencies
- `is_node_critical(name)`: Check criticality
- `should_continue(state)`: Conditional routing
- `reset_all_nodes()`: Reset node status

## Execution Flow

```
pdf_extraction
      ↓
auth_integrations
      ↓
domain_api_design
      ↓
behavior_quality
      ↓
diagram_generation
      ↓
output_composition
      ↓
    END
```

## Usage Examples

### Create a Workflow Graph
```python
from graph import WorkflowGraph, create_workflow_graph

# Using factory class
graph_builder = WorkflowGraph()
graph = graph_builder.create_sequential_workflow_graph()

# Using convenience function
graph = create_workflow_graph()
```

### Access Nodes
```python
from nodes import NodeManager

manager = NodeManager()
pdf_node = manager.get_node("pdf_extraction")
all_nodes_info = manager.get_nodes_info()
execution_order = manager.get_execution_order()
```

### Create Custom Node
```python
from nodes import BaseNode
from state.models import HLDState

class CustomNode(BaseNode):
    def __init__(self):
        super().__init__(
            name="custom_node",
            description="Custom node description",
            critical=False
        )
        # Initialize your logic

    def execute_logic(self, hld_state: HLDState):
        # Implement your logic
        return result
```

## Changes Made

- ✅ Removed old `workflow/graph.py` and `workflow/nodes.py`
- ✅ Removed old `workflow/nodes/` folder
- ✅ Created root-level `graph.py` for easy access
- ✅ Created root-level `nodes/` folder with all node definitions
- ✅ Updated imports to use new structure
- ✅ Maintained backward compatibility with convenience functions
- ✅ Cleaned up unnecessary files and documentation

## Benefits

1. **Clarity**: Clear separation between graph definition and node implementations
2. **Accessibility**: Root-level graph file for easy visualization and access
3. **Modularity**: Each node is independently defined and testable
4. **Scalability**: Easy to add new nodes without modifying existing code
5. **Maintainability**: Single responsibility per file
6. **Extensibility**: Base class pattern for creating custom nodes
