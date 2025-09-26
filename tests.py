# tests.py - Comprehensive test suite for LangGraph HLD Generator
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test imports
from state.models import HLDState, ProcessingStatus
from state.schema import WorkflowInput, ConfigSchema, create_initial_state
from workflow import create_hld_workflow
from agent import (
    PDFExtractionAgent,
    AuthIntegrationsAgent,
    DomainAPIAgent,
    BehaviorQualityAgent,
    DiagramAgent,
    OutputAgent
)

class TestStateModels:
    """Test state management models"""
    
    def test_hld_state_creation(self):
        """Test HLD state creation and basic operations"""
        state = HLDState(pdf_path="test.pdf", requirement_name="test")
        
        assert state.pdf_path == "test.pdf"
        assert state.requirement_name == "test"
        assert not state.has_errors()
        assert len(state.errors) == 0
    
    def test_state_status_updates(self):
        """Test status update functionality"""
        state = HLDState(pdf_path="test.pdf")
        
        state.update_status("test_stage", "processing", "Test message")
        assert "test_stage" in state.status
        assert state.status["test_stage"].status == "processing"
        assert state.status["test_stage"].message == "Test message"
        
        state.update_status("test_stage", "completed")
        assert state.is_stage_completed("test_stage")
    
    def test_error_handling(self):
        """Test error and warning handling"""
        state = HLDState(pdf_path="test.pdf")
        
        state.add_error("Test error")
        assert state.has_errors()
        assert "Test error" in state.errors
        
        state.add_warning("Test warning")
        assert "Test warning" in state.warnings

class TestWorkflowSchema:
    """Test workflow schema and validation"""
    
    def test_config_schema_validation(self):
        """Test configuration schema validation"""
        # Valid config
        config = ConfigSchema(
            render_images=True,
            image_format="png",
            renderer="kroki",
            theme="default"
        )
        assert config.render_images is True
        assert config.image_format == "png"
        
        # Invalid image format should raise validation error
        with pytest.raises(ValueError):
            ConfigSchema(image_format="invalid")
    
    def test_workflow_input_validation(self):
        """Test workflow input validation"""
        config = ConfigSchema()
        
        # Valid input
        input_data = WorkflowInput(
            pdf_path="test.pdf",
            config=config
        )
        assert input_data.pdf_path == "test.pdf"
        
        # Invalid PDF path should raise validation error
        with pytest.raises(ValueError):
            WorkflowInput(pdf_path="test.txt")
    
    def test_initial_state_creation(self):
        """Test initial state creation"""
        config = ConfigSchema()
        state = create_initial_state("test.pdf", config)
        
        assert state.pdf_path == "test.pdf"
        assert state.requirement_name == "test"
        assert len(state.status) > 0  # Should have workflow stages

class TestAgents:
    """Test individual agents"""
    
    @patch('agent.base_agent.genai')
    def test_pdf_agent_initialization(self, mock_genai):
        """Test PDF extraction agent initialization"""
        with patch.dict('os.environ', {'GEMINI_API_KEY_4': 'test-key'}):
            agent = PDFExtractionAgent()
            assert agent.api_key == 'test-key'
            mock_genai.configure.assert_called_with(api_key='test-key')
    
    @patch('agent.base_agent.genai')
    def test_auth_agent_initialization(self, mock_genai):
        """Test authentication agent initialization"""
        with patch.dict('os.environ', {'GEMINI_API_KEY_1': 'test-key'}):
            agent = AuthIntegrationsAgent()
            assert agent.api_key == 'test-key'
    
    def test_agent_system_prompts(self):
        """Test that agents have proper system prompts"""
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            with patch('agent.base_agent.genai'):
                pdf_agent = PDFExtractionAgent()
                auth_agent = AuthIntegrationsAgent()
                domain_agent = DomainAPIAgent()
                behavior_agent = BehaviorQualityAgent()
                
                assert "PDF PRD" in pdf_agent.get_system_prompt()
                assert "authentication" in auth_agent.get_system_prompt()
                assert "domain" in domain_agent.get_system_prompt()
                assert "behavior" in behavior_agent.get_system_prompt()

class TestWorkflow:
    """Test LangGraph workflow functionality"""
    
    def test_workflow_creation(self):
        """Test workflow creation with different types"""
        sequential_workflow = create_hld_workflow("sequential")
        parallel_workflow = create_hld_workflow("parallel")
        conditional_workflow = create_hld_workflow("conditional")
        
        assert sequential_workflow.workflow_type == "sequential"
        assert parallel_workflow.workflow_type == "parallel"
        assert conditional_workflow.workflow_type == "conditional"
    
    def test_workflow_info(self):
        """Test workflow information retrieval"""
        workflow = create_hld_workflow("sequential")
        info = workflow.get_workflow_info()
        
        assert "workflow_type" in info
        assert "nodes" in info
        assert len(info["nodes"]) == 6  # Should have 6 workflow stages
        assert "pdf_extraction" in info["nodes"]
        assert "output_composition" in info["nodes"]

class TestIntegration:
    """Integration tests with mocked components"""
    
    @patch('agent.base_agent.genai')
    def test_pdf_extraction_flow(self, mock_genai):
        """Test PDF extraction with mocked LLM"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "markdown": "# Test Requirements\nThis is a test document.",
            "meta": {"title": "Test", "version": "1.0", "date": "2024-01"}
        })
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(b"fake pdf content")
            tmp_path = tmp_file.name
        
        try:
            with patch.dict('os.environ', {'GEMINI_API_KEY_4': 'test-key'}):
                agent = PDFExtractionAgent()
                state = HLDState(pdf_path=tmp_path, requirement_name="test")
                
                result = agent.process(state)
                
                assert result["success"] is True
                assert state.extracted is not None
                assert state.extracted.markdown == "# Test Requirements\nThis is a test document."
                assert state.is_stage_completed("pdf_extraction")
        
        finally:
            Path(tmp_path).unlink()
    
    @patch('agent.base_agent.genai')
    def test_auth_integration_flow(self, mock_genai):
        """Test authentication and integrations analysis"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "authentication": {
                "actors": ["User", "Admin"],
                "flows": ["OAuth2", "JWT"],
                "idp_options": ["Auth0", "Okta"],
                "threats": ["CSRF", "XSS"]
            },
            "integrations": [
                {
                    "system": "Payment Gateway",
                    "purpose": "Process payments",
                    "protocol": "REST",
                    "auth": "API Key",
                    "endpoints": ["/api/payment"],
                    "data_contract": {
                        "inputs": ["amount", "currency"],
                        "outputs": ["transaction_id", "status"]
                    }
                }
            ]
        })
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict('os.environ', {'GEMINI_API_KEY_1': 'test-key'}):
            agent = AuthIntegrationsAgent()
            state = HLDState(pdf_path="test.pdf")
            state.extracted = Mock()
            state.extracted.markdown = "Test requirements"
            
            result = agent.process(state)
            
            assert result["success"] is True
            assert state.authentication is not None
            assert len(state.authentication.actors) == 2
            assert len(state.integrations) == 1
            assert state.integrations[0].system == "Payment Gateway"

class TestUtilities:
    """Test utility functions"""
    
    def test_diagram_converter(self):
        """Test diagram plan to text conversion"""
        from utils.diagram_converter import diagram_plan_to_text
        
        plan = {
            "class": {
                "classes": ["User", "Order"],
                "relationships": ["User --> Order : creates"]
            },
            "sequences": [
                {
                    "title": "Login Flow",
                    "actors": ["User", "System"],
                    "steps": [
                        {"from": "User", "to": "System", "message": "Login request"}
                    ]
                }
            ]
        }
        
        result = diagram_plan_to_text(plan)
        
        assert "error" not in result
        assert "class_text" in result
        assert "sequence_texts" in result
        assert "classDiagram" in result["class_text"]
        assert "sequenceDiagram" in result["sequence_texts"][0]
    
    def test_risk_heatmap_generation(self):
        """Test risk heatmap generation"""
        from utils.risk_heatmap import generate_risk_heatmap
        
        risks = [
            {"id": "R01", "desc": "Test risk", "impact": 3, "likelihood": 4},
            {"id": "R02", "desc": "Another risk", "impact": 5, "likelihood": 2}
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            result_path = generate_risk_heatmap(risks, tmp_path)
            assert Path(result_path).exists()
            assert Path(result_path).suffix == ".png"
        
        finally:
            Path(tmp_path).unlink(missing_ok=True)

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_missing_api_key(self):
        """Test behavior when API key is missing"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Missing.*API_KEY"):
                PDFExtractionAgent()
    
    def test_invalid_pdf_path(self):
        """Test handling of invalid PDF paths"""
        with patch.dict('os.environ', {'GEMINI_API_KEY_4': 'test-key'}):
            with patch('agent.base_agent.genai'):
                agent = PDFExtractionAgent()
                state = HLDState(pdf_path="nonexistent.pdf")
                
                result = agent.process(state)
                
                assert result["success"] is False
                assert "Invalid PDF path" in result["error"]
                assert state.has_errors()
    
    def test_llm_failure_handling(self):
        """Test handling of LLM failures"""
        with patch.dict('os.environ', {'GEMINI_API_KEY_1': 'test-key'}):
            with patch('agent.base_agent.genai') as mock_genai:
                # Mock LLM to raise an exception
                mock_model = Mock()
                mock_model.generate_content.side_effect = Exception("LLM Error")
                mock_genai.GenerativeModel.return_value = mock_model
                
                agent = AuthIntegrationsAgent()
                state = HLDState(pdf_path="test.pdf")
                state.extracted = Mock()
                state.extracted.markdown = "Test"
                
                result = agent.process(state)
                
                assert result["success"] is False
                assert "LLM call failed" in result["error"]

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])