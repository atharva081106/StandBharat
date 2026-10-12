import pytest
import uuid
from unittest.mock import patch, MagicMock
from app.agents.specialized.content_writer_agent import ContentWriterAgent
from app.agents.context import AgentContext
from app.models.all_models import ContentProject, ContentBrief

def test_content_writer_agent_missing_brief():
    agent = ContentWriterAgent()
    context = AgentContext(
        run_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        input_data={}
    )
    result = agent.execute(context)
    assert result.status == "FAILED"
    assert "Missing brief_id" in result.error

@patch('app.agents.specialized.content_writer_agent.SessionLocal')
@patch('app.agents.specialized.content_writer_agent.ai_gateway.generate')
def test_content_writer_agent_valid_output(mock_generate, mock_session):
    agent = ContentWriterAgent()
    
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_brief = ContentBrief(id=uuid.uuid4(), content_project_id=uuid.uuid4(), content_type="blog", title="T")
    mock_project = ContentProject(id=mock_brief.content_project_id)
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_brief, mock_project]
    
    context = AgentContext(
        run_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        input_data={"brief_id": str(mock_brief.id)}
    )
    
    mock_res = MagicMock()
    mock_res.content = '{"title": "Valid Title", "body": "Valid Body", "metadata": {}}'
    mock_res.info.provider = "test"
    mock_generate.return_value = mock_res
    
    result = agent.execute(context)
    if result.status == "FAILED":
        print(f"FAILED WITH ERROR: {result.error}")
    assert result.status == "SUCCESS"
    assert "draft_id" in result.output_data

@patch('app.agents.specialized.content_writer_agent.SessionLocal')
@patch('app.agents.specialized.content_writer_agent.ai_gateway.generate')
def test_content_writer_agent_invalid_json(mock_generate, mock_session):
    agent = ContentWriterAgent()
    
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_brief = ContentBrief(id=uuid.uuid4(), content_project_id=uuid.uuid4(), content_type="blog", title="T")
    mock_project = ContentProject(id=mock_brief.content_project_id)
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_brief, mock_project]
    
    context = AgentContext(
        run_id=uuid.uuid4(),
        workspace_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        input_data={"brief_id": str(mock_brief.id)}
    )
    
    mock_res = MagicMock()
    mock_res.content = 'Not a JSON'
    mock_res.info.provider = "test"
    mock_generate.return_value = mock_res
    
    result = agent.execute(context)
    assert result.status == "FAILED"
