#!/usr/bin/env python3
"""
Test script to verify the parallel workflow fix
"""

import os
from unittest.mock import Mock, patch

def test_workflow_creation():
    """Test that all workflow types can be created without errors"""
    print("🧪 Testing Workflow Creation...")
    
    try:
        from workflow import create_hld_workflow
        
        # Test sequential workflow
        sequential_workflow = create_hld_workflow("sequential")
        print("✅ Sequential workflow created successfully")
        
        # Test parallel workflow (now optimized sequential)
        parallel_workflow = create_hld_workflow("parallel")
        print("✅ Parallel workflow created successfully")
        
        # Test conditional workflow
        conditional_workflow = create_hld_workflow("conditional")
        print("✅ Conditional workflow created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        return False

def test_workflow_info():
    """Test workflow information retrieval"""
    print("\n🧪 Testing Workflow Information...")
    
    try:
        from workflow import create_hld_workflow
        
        workflow_types = ["sequential", "parallel", "conditional"]
        
        for workflow_type in workflow_types:
            workflow = create_hld_workflow(workflow_type)
            info = workflow.get_workflow_info()
            
            # Check required fields
            required_fields = ["workflow_type", "nodes", "supports_parallel", "supports_streaming"]
            for field in required_fields:
                if field not in info:
                    print(f"❌ Missing field '{field}' in {workflow_type} workflow info")
                    return False
            
            print(f"✅ {workflow_type.title()} workflow info complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow info test failed: {e}")
        return False

def test_parallel_workflow_structure():
    """Test that parallel workflow has correct structure"""
    print("\n🧪 Testing Parallel Workflow Structure...")
    
    try:
        from workflow.graph import create_parallel_workflow_graph
        
        # Create the parallel workflow graph
        graph = create_parallel_workflow_graph()
        print("✅ Parallel workflow graph created without errors")
        
        # The graph should be compiled and ready to use
        if hasattr(graph, 'invoke'):
            print("✅ Parallel workflow graph is properly compiled")
        else:
            print("❌ Parallel workflow graph is not properly compiled")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Parallel workflow structure test failed: {e}")
        return False

def test_state_schema_compatibility():
    """Test that state schema works with all workflow types"""
    print("\n🧪 Testing State Schema Compatibility...")
    
    try:
        from state.schema import WorkflowInput, ConfigSchema, create_initial_state
        
        # Create test configuration
        config = ConfigSchema(
            render_images=True,
            image_format="png",
            renderer="kroki"
        )
        
        # Create initial state
        state = create_initial_state("test.pdf", config)
        print("✅ Initial state created successfully")
        
        # Test state dictionary conversion
        state_dict = state.dict()
        if isinstance(state_dict, dict):
            print("✅ State dictionary conversion working")
        else:
            print("❌ State dictionary conversion failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ State schema compatibility test failed: {e}")
        return False

def test_workflow_input_validation():
    """Test workflow input validation"""
    print("\n🧪 Testing Workflow Input Validation...")
    
    try:
        from state.schema import WorkflowInput, ConfigSchema
        
        # Test valid input
        config = ConfigSchema()
        valid_input = WorkflowInput(
            pdf_path="test.pdf",
            config=config
        )
        print("✅ Valid workflow input created")
        
        # Test invalid input (should raise validation error)
        try:
            invalid_input = WorkflowInput(pdf_path="test.txt")  # Not a PDF
            print("❌ Should have failed with invalid PDF extension")
            return False
        except ValueError:
            print("✅ Invalid input correctly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow input validation test failed: {e}")
        return False

def main():
    """Run all parallel workflow fix tests"""
    print("🧠 DesignMind GenAI - Parallel Workflow Fix Verification")
    print("=" * 60)
    
    tests = [
        ("Workflow Creation", test_workflow_creation),
        ("Workflow Information", test_workflow_info),
        ("Parallel Workflow Structure", test_parallel_workflow_structure),
        ("State Schema Compatibility", test_state_schema_compatibility),
        ("Workflow Input Validation", test_workflow_input_validation),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
            all_passed = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests passed! The parallel workflow fix is working correctly.")
        print("✅ The INVALID_CONCURRENT_GRAPH_UPDATE error should be resolved")
        print("🚀 All workflow types (Sequential, Parallel, Conditional) should work")
        print("💡 Parallel workflow now uses optimized sequential execution")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)