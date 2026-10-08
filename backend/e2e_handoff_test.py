import uuid
from app.db.session import SessionLocal
from app.models.all_models import Workspace, Brand, AgentRun, AgentHandoff, User

def test_handoff_flow():
    print("--- Testing AgentHandoff Model Flow ---")
    db = SessionLocal()
    try:
        # 1. Setup Tenant
        u = User(email=f"handoff_user_{uuid.uuid4().hex[:8]}@example.com", name="Handoff Tester")
        db.add(u)
        db.flush()
        
        ws = Workspace(name="Handoff Workspace", slug=f"handoff-{uuid.uuid4().hex[:6]}", owner_id=u.id)
        db.add(ws)
        db.flush()
        
        b = Brand(name="Handoff Brand", workspace_id=ws.id)
        db.add(b)
        db.flush()
        print(f"Tenant Created. Brand ID: {b.id}")
        
        # 2. Agent 1: Content Strategy (Generates a brief)
        print("\n[Step 1] Content Strategy Agent runs...")
        run_strategy = AgentRun(
            workspace_id=ws.id, 
            brand_id=b.id, 
            agent_id="content_strategy", 
            status="COMPLETED",
            output={"topic": "AI Marketing", "brief_id": "b_123"}
        )
        db.add(run_strategy)
        db.flush()
        
        # Handoff to Writer
        print("[Handoff] Strategy -> Writer")
        run_writer = AgentRun(
            workspace_id=ws.id, 
            brand_id=b.id, 
            agent_id="writer", 
            status="QUEUED"
        )
        db.add(run_writer)
        db.flush()
        
        handoff_1 = AgentHandoff(
            workspace_id=ws.id,
            brand_id=b.id,
            source_agent="content_strategy",
            destination_agent="writer",
            source_run_id=run_strategy.id,
            destination_run_id=run_writer.id,
            input_context={"brief_id": "b_123"}
        )
        db.add(handoff_1)
        db.flush()
        
        # 3. Agent 2: Writer (Writes article)
        print("[Step 2] Writer Agent runs...")
        run_writer.status = "COMPLETED"
        run_writer.output = {"article_text": "AI is changing marketing...", "article_id": "a_456"}
        db.flush()
        
        # Handoff to Designer
        print("[Handoff] Writer -> Designer")
        run_designer = AgentRun(
            workspace_id=ws.id, 
            brand_id=b.id, 
            agent_id="designer", 
            status="QUEUED"
        )
        db.add(run_designer)
        db.flush()
        
        handoff_2 = AgentHandoff(
            workspace_id=ws.id,
            brand_id=b.id,
            source_agent="writer",
            destination_agent="designer",
            source_run_id=run_writer.id,
            destination_run_id=run_designer.id,
            input_context={"article_id": "a_456"}
        )
        db.add(handoff_2)
        db.flush()
        
        # 4. Agent 3: Designer (Creates images)
        print("[Step 3] Designer Agent runs...")
        run_designer.status = "COMPLETED"
        run_designer.output = {"image_urls": ["img1.png", "img2.png"]}
        db.commit()
        
        # 5. Verification
        print("\n--- Verifying Handoff Chain ---")
        handoffs = db.query(AgentHandoff).filter(AgentHandoff.brand_id == b.id).order_by(AgentHandoff.id).all()
        assert len(handoffs) == 2, "Should have 2 handoffs"
        assert handoffs[0].source_agent == "content_strategy"
        assert handoffs[0].destination_agent == "writer"
        assert handoffs[1].source_agent == "writer"
        assert handoffs[1].destination_agent == "designer"
        
        print("Chain verified:")
        print(f" {handoffs[0].source_agent} [Run {str(handoffs[0].source_run_id)[:8]}] ->")
        print(f" {handoffs[0].destination_agent} [Run {str(handoffs[0].destination_run_id)[:8]}] ->")
        print(f" {handoffs[1].destination_agent} [Run {str(handoffs[1].destination_run_id)[:8]}]")
        
        print("\n✅ MULTI-AGENT HANDOFF VERIFIED SUCCESSFULLY")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_handoff_flow()
