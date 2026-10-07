import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import User, Workspace, WorkspaceMember, Brand, Opportunity, ActivityEvent, UserRole, BrandVoice, Audience, Product, Positioning, Goal, Competitor, BrandStrategy, MetricSnapshot, AgentRun, ContentProject, ContentBrief, ContentDraft, ContentApproval
from app.core.security import get_password_hash

def seed_demo():
    db: Session = SessionLocal()
    try:
        # Create user
        email = "demo@standbharat.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name="Demo User", hashed_password=get_password_hash("password123"))
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create Workspace
        ws = db.query(Workspace).filter(Workspace.name == "Demo Workspace").first()
        if not ws:
            ws = Workspace(name="Demo Workspace", slug="demo-workspace", owner_id=user.id)
            db.add(ws)
            db.commit()
            db.refresh(ws)
            
            # Add member
            member = WorkspaceMember(user_id=user.id, workspace_id=ws.id, role=UserRole.OWNER)
            db.add(member)
            db.commit()

        # Create Brand
        brand = db.query(Brand).filter(Brand.workspace_id == ws.id).first()
        if not brand:
            brand = Brand(
                name="Acme Corp", 
                workspace_id=ws.id, 
                website_url="https://acme.com", 
                industry="Technology",
                category="B2B SaaS",
                location="San Francisco, CA",
                mission="To revolutionize how teams collaborate through AI.",
                vision="A world where work is seamless and creative.",
                values="Innovation, Integrity, Impact",
                tagline="Work smarter, not harder."
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)
            
            # Seed Brand Voice
            db.add(BrandVoice(
                brand_id=brand.id,
                tone="Professional but approachable",
                personality="Helpful expert",
                writing_style="Clear, concise, active voice",
                preferred_language="US English",
                formality="Semi-formal",
                words_to_use="efficiency, collaboration, AI-driven, seamless",
                words_to_avoid="cheap, hack, trick"
            ))
            
            # Seed Audience
            db.add(Audience(
                brand_id=brand.id,
                name="Tech Leads",
                description="Engineering and IT managers looking for productivity tools.",
                demographics="Age 30-50, Urban, High Income",
                pain_points="Too many disconnected tools, low team visibility.",
                goals="Streamline workflows, reduce tool fatigue."
            ))
            
            # Seed Product
            db.add(Product(
                brand_id=brand.id,
                name="Acme AI Assistant",
                description="An AI powered workspace companion.",
                category="Software",
                price="$20/mo",
                value_proposition="Saves 10 hours a week per employee."
            ))
            
            # Seed Positioning
            db.add(Positioning(
                brand_id=brand.id,
                positioning_statement="For tech teams who need to move fast, Acme is the AI assistant that connects all your tools into one seamless interface.",
                unique_value_proposition="The only AI assistant with native integrations to 50+ dev tools.",
                key_messages="Move fast. Don't break things.",
                market_category="AI Productivity"
            ))
            
            # Seed Goals
            db.add(Goal(
                brand_id=brand.id,
                goal="Increase Q3 Revenue",
                target_value="$1M",
                current_value="$750k",
                timeframe="Q3 2026",
                priority=1
            ))
            
            # Seed Competitors
            db.add(Competitor(
                brand_id=brand.id,
                name="Globex Corp",
                website="https://globex.example",
                description="Legacy enterprise productivity software.",
                strengths="Large enterprise footprint.",
                weaknesses="Slow, clunky UI, no AI features."
            ))
            
            # Seed Strategy
            db.add(BrandStrategy(
                brand_id=brand.id,
                business_strategy="Expand into mid-market tech companies.",
                marketing_strategy="Content-led SEO and targeted LinkedIn ads.",
                content_strategy="Publish weekly engineering guides and case studies."
            ))
            
            db.commit()

        # Create Opportunities
        opps = db.query(Opportunity).filter(Opportunity.workspace_id == ws.id).all()
        if not opps:
            opp1 = Opportunity(
                workspace_id=ws.id, brand_id=brand.id, title="Optimize Landing Page CTA",
                impact="High", confidence="High", effort="Low", priority=10, source="System"
            )
            opp2 = Opportunity(
                workspace_id=ws.id, brand_id=brand.id, title="Launch Retargeting Campaign",
                impact="High", confidence="Medium", effort="Medium", priority=5, source="Agent"
            )
            db.add_all([opp1, opp2])
            db.commit()
            
        # Create Activity
        activities = db.query(ActivityEvent).filter(ActivityEvent.workspace_id == ws.id).all()
        if not activities:
            a1 = ActivityEvent(
                workspace_id=ws.id, brand_id=brand.id, type="SYSTEM", description="Workspace initialized"
            )
            a2 = ActivityEvent(
                workspace_id=ws.id, brand_id=brand.id, type="CAMPAIGN", description="Launched Q3 Campaign"
            )
            db.add_all([a1, a2])
            db.commit()
            
        # Create MetricSnapshots
        metrics = db.query(MetricSnapshot).filter(MetricSnapshot.workspace_id == ws.id).all()
        if not metrics:
            m1 = MetricSnapshot(workspace_id=ws.id, brand_id=brand.id, metric_name="Website Visitors", value=15000.0)
            m2 = MetricSnapshot(workspace_id=ws.id, brand_id=brand.id, metric_name="Conversion Rate", value=2.5)
            m3 = MetricSnapshot(workspace_id=ws.id, brand_id=brand.id, metric_name="CPA", value=45.50)
            db.add_all([m1, m2, m3])
            db.commit()
            
        # Create Demo AgentRun
        runs = db.query(AgentRun).filter(AgentRun.workspace_id == ws.id).all()
        if not runs:
            r1 = AgentRun(
                workspace_id=ws.id, brand_id=brand.id, agent_type="analytics", status="SUCCESS",
                output_data={"summary": "[DEMO DATA] Analytics run.", "signals": []}
            )
            db.add(r1)
            db.commit()

        # Create Content Models (Phase 12 Demo)
        content_projects = db.query(ContentProject).filter(ContentProject.workspace_id == ws.id).all()
        if not content_projects:
            demo_opp = db.query(Opportunity).filter(Opportunity.workspace_id == ws.id).first()
            cp = ContentProject(
                workspace_id=ws.id,
                brand_id=brand.id,
                opportunity_id=demo_opp.id if demo_opp else None,
                title="[DEMO] Q3 Launch Blog Post",
                objective="Drive awareness for the new Q3 features",
                content_type="BLOG_POST",
                status="IN_REVIEW",
                created_by=user.id
            )
            db.add(cp)
            db.commit()
            db.refresh(cp)

            cb = ContentBrief(
                content_project_id=cp.id,
                workspace_id=ws.id,
                brand_id=brand.id,
                title="[DEMO] Q3 Launch Brief",
                objective="Highlight top 3 new features",
                target_audience="Tech Leads",
                content_type="BLOG_POST",
                status="APPROVED"
            )
            db.add(cb)
            db.commit()
            db.refresh(cb)

            cd = ContentDraft(
                content_project_id=cp.id,
                brief_id=cb.id,
                workspace_id=ws.id,
                brand_id=brand.id,
                content_type="BLOG_POST",
                title="Top 3 Features in Q3",
                body="Here is the demo content body...",
                status="IN_REVIEW",
                generated_by="content_writer_agent"
            )
            db.add(cd)
            db.commit()
            db.refresh(cd)

            ca = ContentApproval(
                content_project_id=cp.id,
                content_draft_id=cd.id,
                workspace_id=ws.id,
                brand_id=brand.id,
                requested_by=user.id,
                status="PENDING"
            )
            db.add(ca)
            db.commit()

        print("Demo seed completed successfully.")
        print(f"Login with: {email} / password123")

    finally:
        db.close()

if __name__ == "__main__":
    seed_demo()
