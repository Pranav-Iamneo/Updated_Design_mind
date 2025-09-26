#!/usr/bin/env python3
"""
Test script to verify the agent fix for update_state_status
"""

import os
from unittest.mock import Mock, patch

def test_auth_agent_fix():
    """Test that AuthIntegrationsAgent works correctly"""
    print("🧪 Testing AuthIntegrationsAgent fix...")
    
    try:
        # Mock environment variables
        with patch.dict('os.environ', {'GEMINI_API_KEY_1': 'test-key'}):
            with patch('agent.base_agent.genai'):
                from agent.auth_agent import AuthIntegrationsAgent
                from state.models import HLDState, ExtractedContent
                
                # Create agent
                agent = AuthIntegrationsAgent()
                print("✅ Agent created successfully")
                
                # Create test state
                state = HLDState(pdf_path="test.pdf", requirement_name="test")
                state.extracted = ExtractedContent(markdown="Test requirements")
                print("✅ Test state created")
                
                # Mock LLM response
                mock_response = Mock()
                mock_response.text = '{"authentication": {"actors": ["User"], "flows": ["OAuth"], "idp_options": ["Auth0"], "threats": ["XSS"]}, "integrations": []}'
                agent.model.generate_content.return_value = mock_response
                
                # Test the process method
                result = agent.process(state)
                print("✅ Process method executed without errors")
                
                # Check if state was updated correctly
                if state.authentication is not None:
                    print("✅ State authentication data updated")
                else:
                    print("❌ State authentication data not updated")
                    return False
                
                # Check if status was updated
                if "auth_integrations" in state.status:
                    print("✅ Status tracking working correctly")
                else:
                    print("❌ Status tracking failed")
                    return False
                
                return True
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_all_agents():
    """Test all agents for similar issues"""
    print("🔍 Testing all agents for update_state_status issues...")
    
    agents_to_test = [
        ("PDFExtractionAgent", "GEMINI_API_KEY_4"),
        ("AuthIntegrationsAgent", "GEMINI_API_KEY_1"),
        ("DomainAPIAgent", "GEMINI_API_KEY_3"),
        ("BehaviorQualityAgent", "GEMINI_API_KEY_2"),
    ]
    
    all_passed = True
    
    for agent_name, api_key in agents_to_test:
        try:
            with patch.dict('os.environ', {api_key: 'test-key'}):
                with patch('agent.base_agent.genai'):
                    # Import the agent class
                    if agent_name == "PDFExtractionAgent":
                        from agent.pdf_agent import PDFExtractionAgent as AgentClass
                    elif agent_name == "AuthIntegrationsAgent":
                        from agent.auth_agent import AuthIntegrationsAgent as AgentClass
                    elif agent_name == "DomainAPIAgent":
                        from agent.domain_agent import DomainAPIAgent as AgentClass
                    elif agent_name == "BehaviorQualityAgent":
                        from agent.behavior_agent import BehaviorQualityAgent as AgentClass
                    
                    # Create agent
                    agent = AgentClass()
                    print(f"✅ {agent_name} created successfully")
                    
        except Exception as e:
            print(f"❌ {agent_name} failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🧠 DesignMind GenAI - Agent Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Auth Agent Fix", test_auth_agent_fix),
        ("All Agents Import", test_all_agents),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
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
    print(f"\n{'='*50}")
    print("📋 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests passed! The agent fix is working correctly.")
        print("✅ The 'str' object has no attribute 'update_status' error should be resolved")
        print("🚀 Try running: streamlit run main.py")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)