import json
from app.core.celery_app import celery_app

@celery_app.task
def dummy_agent_task(task_id: str):
    print(f"Executing agent task {task_id}")
    return {"status": "success", "task_id": task_id}

@celery_app.task
def generate_core_brand_strategy(workspace_id: str, brand_id: str):
    from app.db.session import SessionLocal
    from app.services.brand_context import BrandContextService
    from app.models.all_models import BrandStrategy, Brand
    from app.ai.gateway import ai_gateway
    from app.ai.schemas import AIRequestMessage
    from app.ai.exceptions import AINotConfiguredException
    import uuid
    
    db = SessionLocal()
    brand_uuid = None
    try:
        try:
            workspace_uuid = uuid.UUID(workspace_id)
            brand_uuid = uuid.UUID(brand_id)
        except ValueError:
            return {"status": "error", "reason": "invalid_uuid"}

        brand_strategy = db.query(BrandStrategy).filter_by(brand_id=brand_uuid).first()
        if not brand_strategy:
            brand_strategy = BrandStrategy(brand_id=brand_uuid)
            db.add(brand_strategy)
            
        # Check if already generated and valid, to avoid overwriting user edits
        if brand_strategy.business_strategy and brand_strategy.business_strategy not in ("PARTIAL", "NOT_CONFIGURED", "FAILED", "QUEUED", "RUNNING"):
            # Trigger documents just in case they were missing
            generate_foundational_documents.delay(workspace_id, brand_id)
            return {"status": "skipped", "reason": "already_exists"}

        brand_strategy.business_strategy = "RUNNING"
        db.commit()

        context = BrandContextService.get_unified_context(db, workspace_uuid, brand_uuid)
        
        # Ensure we have website analysis
        if not context.get("website_analysis"):
            brand_strategy.business_strategy = "PARTIAL"
            db.commit()
            return {"status": "partial", "reason": "insufficient_research"}
            
        try:
            ai_gateway._get_provider()
        except AINotConfiguredException:
            brand_strategy.business_strategy = "NOT_CONFIGURED"
            db.commit()
            return {"status": "not_configured", "reason": "ai_not_configured"}
            
        prompt = f"""
        Generate a comprehensive core Brand Strategy based on the following brand context:
        {json.dumps(context, indent=2)}
        
        Return a JSON object matching this exact structure:
        {{
            "business_strategy": "string",
            "marketing_strategy": "string",
            "content_strategy": "string",
            "channel_strategy": "string",
            "growth_strategy": "string",
            "campaign_strategy": "string"
        }}
        """
        
        res = ai_gateway.generate(
            messages=[
                AIRequestMessage(role="system", content="You are an expert Chief Marketing Officer. Output valid JSON only."),
                AIRequestMessage(role="user", content=prompt)
            ]
        )
        
        content = res.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed = json.loads(content.strip(), strict=False)
        brand_strategy.business_strategy = parsed.get("business_strategy", "")
        brand_strategy.marketing_strategy = parsed.get("marketing_strategy", "")
        brand_strategy.content_strategy = parsed.get("content_strategy", "")
        brand_strategy.channel_strategy = parsed.get("channel_strategy", "")
        brand_strategy.growth_strategy = parsed.get("growth_strategy", "")
        brand_strategy.campaign_strategy = parsed.get("campaign_strategy", "")
        
        db.commit()
        
        # Trigger foundational documents generation
        generate_foundational_documents.delay(workspace_id, brand_id)
        
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        print(f"Error generating strategy: {e}")
        from app.ai.exceptions import AIAuthException
        
        # Ensure we have a strategy object to mark as failed/not configured
        status, reason = "error", str(e)
        if brand_uuid:
            brand_strategy = db.query(BrandStrategy).filter_by(brand_id=brand_uuid).first()
            if not brand_strategy:
                brand_strategy = BrandStrategy(brand_id=brand_uuid)
                db.add(brand_strategy)
                
            if isinstance(e, AIAuthException):
                brand_strategy.business_strategy = "NOT_CONFIGURED"
                status, reason = "not_configured", "invalid_api_key"
            else:
                brand_strategy.business_strategy = "FAILED"
                status, reason = "error", str(e)
                
            db.commit()
        return {"status": status, "reason": reason}
    finally:
        db.close()

@celery_app.task
def generate_foundational_documents(workspace_id: str, brand_id: str):
    from app.db.session import SessionLocal
    from app.services.brand_context import BrandContextService
    from app.models.all_models import StrategyDocument
    from app.ai.gateway import ai_gateway
    from app.ai.schemas import AIRequestMessage
    from app.ai.exceptions import AINotConfiguredException
    import uuid
    import json
    
    db = SessionLocal()
    try:
        try:
            workspace_uuid = uuid.UUID(workspace_id)
            brand_uuid = uuid.UUID(brand_id)
        except ValueError:
            return {"status": "error", "reason": "invalid_uuid"}

        context = BrandContextService.get_unified_context(db, workspace_uuid, brand_uuid)
        if not context.get("website_analysis"):
            return {"status": "partial", "reason": "insufficient_research"}
            
        try:
            ai_gateway._get_provider()
        except AINotConfiguredException:
            # We don't overwrite user edits, but if there's no doc, we mark it NOT_CONFIGURED
            return {"status": "not_configured", "reason": "ai_not_configured"}

        doc_types = [
            ("PRODUCT_INFORMATION", "Product Information Document: Detail the core value proposition, key features, pricing, target audience, and competitive advantages."),
            ("COMPETITOR_ANALYSIS", "Competitor Analysis Document: List direct and indirect competitors, their strengths/weaknesses, positioning, and our strategic differentiation. Do not fabricate facts."),
            ("BRAND_VOICE", "Brand Voice Guide: Define tone, personality, writing style, vocabulary, phrasing rules, and examples of what to sound like vs what not to sound like."),
            ("GROWTH_PLAYBOOK", "Growth Playbook: Propose actionable marketing campaigns, channels to prioritize, metrics to track, and step-by-step growth tactics.")
        ]
        
        results = []
        for d_type, instructions in doc_types:
            doc = db.query(StrategyDocument).filter_by(brand_id=brand_uuid, type=d_type).first()
            if doc and doc.status == "ACTIVE" and doc.content and "NOT_CONFIGURED" not in str(doc.content) and "PARTIAL" not in str(doc.content):
                # Never overwrite user-edited or already generated documents silently
                results.append({"type": d_type, "status": "skipped", "reason": "already_exists"})
                continue
                
            prompt = f"""
            Based on the following Brand Context:
            {json.dumps(context, indent=2)}
            
            Generate the: {instructions}
            
            Return ONLY a valid JSON object with the following structure:
            {{
                "title": "Document Title",
                "executive_summary": "A brief summary",
                "sections": [
                    {{
                        "heading": "Section Heading",
                        "content": "Detailed markdown formatted content for this section"
                    }}
                ]
            }}
            """
            
            try:
                res = ai_gateway.generate(
                    messages=[
                        AIRequestMessage(role="system", content="You are an expert marketing strategist. Output valid JSON only, distinguishing verified facts from inferences."),
                        AIRequestMessage(role="user", content=prompt)
                    ]
                )
                
                content = res.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                    
                parsed_content = json.loads(content.strip(), strict=False)
                
                if not doc:
                    doc = StrategyDocument(
                        workspace_id=workspace_uuid,
                        brand_id=brand_uuid,
                        type=d_type
                    )
                    db.add(doc)
                
                doc.content = parsed_content
                doc.status = "ACTIVE"
                db.commit()
                results.append({"type": d_type, "status": "success"})
            except Exception as e:
                db.rollback()
                from app.ai.exceptions import AIAuthException
                
                # Re-fetch or create to update state
                doc = db.query(StrategyDocument).filter_by(brand_id=brand_uuid, type=d_type).first()
                if not doc:
                    doc = StrategyDocument(workspace_id=workspace_uuid, brand_id=brand_uuid, type=d_type)
                    db.add(doc)
                    
                if isinstance(e, AIAuthException):
                    doc.status = "NOT_CONFIGURED"
                    db.commit()
                    results.append({"type": d_type, "status": "not_configured", "reason": "invalid_api_key"})
                    break # Stop trying other documents if auth fails
                else:
                    doc.status = "FAILED"
                    db.commit()
                    results.append({"type": d_type, "status": "error", "reason": str(e)})

        return {"status": "success", "results": results}
    except Exception as e:
        db.rollback()
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()
