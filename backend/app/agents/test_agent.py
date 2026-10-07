from .base import BaseAgent
from .context import AgentContext
from .result import AgentResult
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException
from app.models.all_models import AIUsageEvent
from app.db.session import SessionLocal
import traceback

class TestAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="test-agent",
            name="Test Agent",
            description="A generic test agent to verify the AI Foundation",
            capabilities=["test"]
        )

    def execute(self, context: AgentContext) -> AgentResult:
        messages = [
            AIRequestMessage(role="system", content="You are a helpful assistant."),
            AIRequestMessage(role="user", content=context.input_data.get("prompt", "Generate a short test response."))
        ]
        
        try:
            response = ai_gateway.generate(messages=messages, max_tokens=100)
            
            # Log usage
            db = SessionLocal()
            try:
                usage = AIUsageEvent(
                    workspace_id=context.workspace_id,
                    brand_id=context.brand_id,
                    user_id=context.user_id,
                    agent_id=self.agent_id, # Can't use UUID here directly unless we define agent_id as string or change model
                    agent_run_id=context.run_id,
                    provider=response.info.provider,
                    model=response.info.model,
                    input_tokens=response.info.input_tokens,
                    output_tokens=response.info.output_tokens,
                    total_tokens=response.info.total_tokens,
                    estimated_cost=response.info.estimated_cost,
                    status="SUCCESS"
                )
                db.add(usage)
                db.commit()
            except Exception as e:
                db.rollback()
            finally:
                db.close()
                
            return AgentResult(status="SUCCESS", output_data={"response": response.content})
            
        except AINotConfiguredException as e:
            return AgentResult(status="NOT_CONFIGURED", error=str(e))
        except Exception as e:
            return AgentResult(status="FAILED", error=f"Error: {str(e)}\n{traceback.format_exc()}")
