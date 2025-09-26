#!/usr/bin/env python3
"""
Test script to verify Pydantic v2 compatibility fixes
"""

def test_pydantic_imports():
    """Test that all Pydantic models can be imported without errors"""
    print("🔍 Testing Pydantic v2 Compatibility...")
    
    try:
        # Test state models import
        from state.models import (
            HLDState, ProcessingStatus, ExtractedContent,
            AuthenticationData, IntegrationData, DomainData,
            BehaviorData, DiagramData, OutputData
        )
        print("✅ State models imported successfully")
        
        # Test schema imports
        from state.schema import (
            ConfigSchema, WorkflowInput, WorkflowOutput,
            create_initial_state
        )
        print("✅ Schema models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_schema_validation():
    """Test ConfigSchema validation with Pydantic v2"""
    print("\n🧪 Testing ConfigSchema validation...")
    
    try:
        from state.schema import ConfigSchema
        
        # Test valid configuration
        config = ConfigSchema(
            render_images=True,
            image_format="png",
            renderer="kroki",
            theme="default"
        )
        print("✅ Valid configuration created successfully")
        
        # Test invalid image format
        try:
            invalid_config = ConfigSchema(image_format="invalid")
            print("❌ Should have failed with invalid image format")
            return False
        except ValueError as e:
            print("✅ Correctly rejected invalid image format")
        
        # Test invalid renderer
        try:
            invalid_config = ConfigSchema(renderer="invalid")
            print("❌ Should have failed with invalid renderer")
            return False
        except ValueError as e:
            print("✅ Correctly rejected invalid renderer")
        
        return True
        
    except Exception as e:
        print(f"❌ ConfigSchema validation failed: {e}")
        return False

def test_workflow_input_validation():
    """Test WorkflowInput validation"""
    print("\n🧪 Testing WorkflowInput validation...")
    
    try:
        from state.schema import WorkflowInput, ConfigSchema
        
        # Test valid input
        config = ConfigSchema()
        input_data = WorkflowInput(
            pdf_path="test.pdf",
            config=config
        )
        print("✅ Valid WorkflowInput created successfully")
        
        # Test invalid PDF path
        try:
            invalid_input = WorkflowInput(pdf_path="test.txt")
            print("❌ Should have failed with invalid PDF path")
            return False
        except ValueError as e:
            print("✅ Correctly rejected invalid PDF path")
        
        return True
        
    except Exception as e:
        print(f"❌ WorkflowInput validation failed: {e}")
        return False

def test_hld_state_creation():
    """Test HLDState model creation and methods"""
    print("\n🧪 Testing HLDState functionality...")
    
    try:
        from state.models import HLDState
        
        # Create HLD state
        state = HLDState(
            pdf_path="test.pdf",
            requirement_name="test"
        )
        print("✅ HLDState created successfully")
        
        # Test status updates
        state.update_status("test_stage", "processing", "Test message")
        if state.status["test_stage"].status == "processing":
            print("✅ Status update working correctly")
        else:
            print("❌ Status update failed")
            return False
        
        # Test error handling
        state.add_error("Test error")
        if state.has_errors() and "Test error" in state.errors:
            print("✅ Error handling working correctly")
        else:
            print("❌ Error handling failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ HLDState functionality failed: {e}")
        return False

def main():
    """Run all Pydantic compatibility tests"""
    print("🧠 DesignMind GenAI - Pydantic v2 Compatibility Test")
    print("=" * 55)
    
    tests = [
        ("Pydantic Imports", test_pydantic_imports),
        ("ConfigSchema Validation", test_config_schema_validation),
        ("WorkflowInput Validation", test_workflow_input_validation),
        ("HLDState Functionality", test_hld_state_creation),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
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
    print(f"\n{'='*55}")
    print("📋 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n{'='*55}")
    if all_passed:
        print("🎉 All Pydantic v2 compatibility tests passed!")
        print("✅ The application should now run without Pydantic errors")
        print("🚀 Try running: streamlit run main.py")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)