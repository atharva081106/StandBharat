import logging
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.all_models import (
    User, Workspace, WorkspaceMember, UserRole, Brand,
    BrandVoice, Positioning, Competitor, Audience, Product, Goal,
    Opportunity, Campaign, WebsiteAnalysis, MetricSnapshot, ActivityEvent,
    TrafficMetrics, SearchMetrics, ContentProject, ContentBrief, ContentDraft, ContentVersion
)
from app.publishing.models import Publication

logger = logging.getLogger(__name__)

DEMO_EMAIL = "demo@standbharat.ai"
DEMO_PASSWORD = "demo"

def ensure_demo_user(db: Session) -> User:
    """
    Ensures that the demo user, workspace, brand, brand-brain, opportunities,
    and campaigns are fully provisioned in the database.
    """
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if not user:
        logger.info(f"Creating demo user: {DEMO_EMAIL}")
        user = User(
            id=uuid.uuid4(),
            email=DEMO_EMAIL,
            name="Demo User",
            hashed_password=get_password_hash(DEMO_PASSWORD)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Verify and update password if needed
        if not verify_password(DEMO_PASSWORD, user.hashed_password):
            user.hashed_password = get_password_hash(DEMO_PASSWORD)
            db.commit()

    # Ensure Workspace
    ws = db.query(Workspace).filter(Workspace.owner_id == user.id).first()
    if not ws:
        ws = db.query(Workspace).filter(Workspace.slug == "demo-workspace").first()
    if not ws:
        logger.info("Creating demo workspace")
        ws = Workspace(
            id=uuid.uuid4(),
            name="StandBharat Demo Workspace",
            slug="demo-workspace",
            owner_id=user.id
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)

    # Ensure Workspace Member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == ws.id,
        WorkspaceMember.user_id == user.id
    ).first()
    if not member:
        member = WorkspaceMember(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            user_id=user.id,
            role=UserRole.OWNER
        )
        db.add(member)
        db.commit()

    # Ensure Brand
    brand = db.query(Brand).filter(Brand.workspace_id == ws.id).first()
    if not brand:
        logger.info("Creating demo brand")
        brand = Brand(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            name="StandBharat Global",
            website_url="https://standbharat.ai",
            industry="AI Marketing & Growth Intelligence",
            description="Continuous marketing operating system with an autonomous AI CMO at the center.",
            status="active"
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)

    # Ensure Brand Voice
    voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
    if not voice:
        voice = BrandVoice(
            id=uuid.uuid4(),
            brand_id=brand.id,
            tone="Visionary & Authoritative",
            personality="Decisive, strategic, high-velocity",
            writing_style="Data-driven and compelling",
            preferred_language="English",
            formality="Professional yet accessible",
            humor="Minimal",
            words_to_use="autonomous, velocity, ROI, strategic, compounding",
            words_to_avoid="synergy, cheap, generic, buzzword",
            messaging_rules="Focus on measurable growth, pipeline attribution, and autonomous efficiency."
        )
        db.add(voice)

    # Ensure Positioning
    pos = db.query(Positioning).filter(Positioning.brand_id == brand.id).first()
    if not pos:
        pos = Positioning(
            id=uuid.uuid4(),
            brand_id=brand.id,
            positioning_statement="The all-in-one AI CMO operating system for high-growth enterprises.",
            unique_value_proposition="Continuous marketing automation across SEO, content, approvals, publishing, and revenue attribution.",
            differentiators="Real-time multi-agent orchestration, integrated compliance guardrails, and automated SEO discovery.",
            market_category="AI Marketing Operating Systems"
        )
        db.add(pos)

    # Ensure Competitors
    if db.query(Competitor).filter(Competitor.brand_id == brand.id).count() == 0:
        competitors = [
            Competitor(
                id=uuid.uuid4(),
                brand_id=brand.id,
                name="HubSpot",
                website="https://hubspot.com",
                description="Legacy inbound marketing platform.",
                strengths="Large ecosystem, enterprise footprint.",
                weaknesses="Heavy manual configuration, fragmented AI tooling."
            ),
            Competitor(
                id=uuid.uuid4(),
                brand_id=brand.id,
                name="Jasper AI",
                website="https://jasper.ai",
                description="AI copy generation tool.",
                strengths="Fast copy generation.",
                weaknesses="Lacks executive CMO orchestration, campaign budgeting, and publication pipelines."
            ),
            Competitor(
                id=uuid.uuid4(),
                brand_id=brand.id,
                name="Copy.ai",
                website="https://copy.ai",
                description="Go-to-market workflow assistant.",
                strengths="Workflow builder.",
                weaknesses="Shallow SEO gap intelligence and no built-in publishing calendar."
            )
        ]
        for c in competitors:
            db.add(c)

    # Ensure Audiences
    if db.query(Audience).filter(Audience.brand_id == brand.id).count() == 0:
        db.add(Audience(
            id=uuid.uuid4(),
            brand_id=brand.id,
            name="Founders & CMOs",
            description="Chief Executives seeking high ROI without scaling large manual marketing agencies.",
            pain_points="Fragmented marketing tools, slow content cycle, inconsistent brand voice.",
            goals="Accelerate organic pipeline and scale multi-channel presence."
        ))

    # Ensure Products
    if db.query(Product).filter(Product.brand_id == brand.id).count() == 0:
        db.add(Product(
            id=uuid.uuid4(),
            brand_id=brand.id,
            name="StandBharat AI Marketing Operating System",
            description="Full-stack AI CMO platform connecting brand brain, strategy, agents, and ROI.",
            category="SaaS / Enterprise Software",
            value_proposition="Autonomous execution from strategy to publication."
        ))

    # Ensure Goals
    if db.query(Goal).filter(Goal.brand_id == brand.id).count() == 0:
        db.add(Goal(
            id=uuid.uuid4(),
            brand_id=brand.id,
            goal="Scale Organic Attributed Pipeline by 300%",
            target_value="$150,000 / mo",
            timeframe="Q4 2026",
            priority=100
        ))

    # Ensure Sample Opportunities
    if db.query(Opportunity).filter(Opportunity.brand_id == brand.id).count() == 0:
        opps = [
            Opportunity(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                title="Scale High-Intent Comparison Articles in AI Marketing",
                description="Deploy 5 targeted comparison pieces against legacy marketing suites to capture searchers with immediate purchase intent.",
                impact="HIGH",
                effort="LOW",
                confidence="HIGH",
                priority=95,
                status="NEW",
                source="AI_CMO"
            ),
            Opportunity(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                title="Automate Founder LinkedIn Thought Leadership",
                description="Publish weekly deep-dives on the shift to agentic marketing to generate direct executive referral loops.",
                impact="HIGH",
                effort="LOW",
                confidence="HIGH",
                priority=90,
                status="NEW",
                source="AI_CMO"
            ),
            Opportunity(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                title="Target Long-Tail Competitor Alternative Keywords",
                description="Capture prospects actively researching migration from expensive legacy tools.",
                impact="MEDIUM",
                effort="LOW",
                confidence="HIGH",
                priority=80,
                status="ACCEPTED",
                source="AI_CMO"
            )
        ]
        for o in opps:
            db.add(o)

    # Ensure Sample Campaigns
    if db.query(Campaign).filter(Campaign.workspace_id == ws.id).count() == 0:
        camps = [
            Campaign(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                name="Q4 AI CMO Enterprise Launch",
                description="Multi-channel campaign driving adoption among high-growth startup leadership.",
                status="ACTIVE",
                budget=5000.0,
                spent=1420.0
            ),
            Campaign(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                name="Organic Search Authority Engine",
                description="Topical authority campaign capturing high-volume enterprise SEO queries.",
                status="ACTIVE",
                budget=3000.0,
                spent=850.0
            )
        ]
        for camp in camps:
            db.add(camp)

    # Ensure Website Analysis
    if db.query(WebsiteAnalysis).filter(WebsiteAnalysis.brand_id == brand.id).count() == 0:
        db.add(WebsiteAnalysis(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            brand_id=brand.id,
            status="COMPLETED",
            url="https://standbharat.ai",
            result_metadata={
                "title": "StandBharat - Autonomous AI CMO Marketing Operating System",
                "description": "Continuous marketing automation across SEO, multi-channel content generation, approval workflows, social publishing, and revenue attribution.",
                "h1": ["The Autonomous Marketing Operating System for Modern Teams"],
                "h2": ["Continuous Strategy", "Multi-Agent Intelligence", "Autonomous Execution", "Closed-Loop Attribution"],
                "keywords": ["ai cmo", "marketing automation", "agentic marketing", "seo automation", "content strategy"],
                "internal_links_count": 28,
                "status_code": 200,
                "ssl": True
            },
            analysis_results={
                "technical_score": 92,
                "seo_health": 88,
                "mobile_responsiveness": "OPTIMAL",
                "content_readability": "HIGH",
                "speed_index": "1.4s"
            }
        ))

    # Ensure Metric Snapshots
    if db.query(MetricSnapshot).filter(MetricSnapshot.brand_id == brand.id).count() == 0:
        metrics = [
            MetricSnapshot(id=uuid.uuid4(), workspace_id=ws.id, brand_id=brand.id, metric_name="MRR", value=42500.0, currency="USD"),
            MetricSnapshot(id=uuid.uuid4(), workspace_id=ws.id, brand_id=brand.id, metric_name="CAC", value=310.0, currency="USD"),
            MetricSnapshot(id=uuid.uuid4(), workspace_id=ws.id, brand_id=brand.id, metric_name="LTV", value=3850.0, currency="USD"),
            MetricSnapshot(id=uuid.uuid4(), workspace_id=ws.id, brand_id=brand.id, metric_name="Organic Traffic", value=18400.0, currency="SESSIONS"),
            MetricSnapshot(id=uuid.uuid4(), workspace_id=ws.id, brand_id=brand.id, metric_name="Signups", value=840.0, currency="COUNT"),
        ]
        for m in metrics:
            db.add(m)

    # Ensure Traffic Metrics (Trailing 14 days)
    if db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == brand.id).count() == 0:
        now = datetime.utcnow()
        traffic_entries = []
        sources = [
            ("google", "organic", "/", 120, 95, 210, 0.65, 8),
            ("google", "organic", "/product", 85, 70, 160, 0.72, 12),
            ("linkedin", "social", "/blog/autonomous-cmo", 90, 80, 130, 0.58, 6),
            ("twitter", "social", "/", 45, 40, 75, 0.50, 3),
            ("direct", "none", "/pricing", 65, 55, 110, 0.78, 15),
        ]
        for days_ago in range(14):
            day_date = now - timedelta(days=days_ago)
            for src, med, lp, sess, users, pv, eng, conv in sources:
                traffic_entries.append(TrafficMetrics(
                    id=uuid.uuid4(),
                    workspace_id=ws.id,
                    brand_id=brand.id,
                    date=day_date,
                    source=src,
                    medium=med,
                    landing_page=lp,
                    sessions=sess + (days_ago * 2),
                    active_users=users + days_ago,
                    pageviews=pv + (days_ago * 3),
                    engagement_rate=eng,
                    conversions=conv
                ))
        for t in traffic_entries:
            db.add(t)

    # Ensure Search Metrics (Trailing 14 days)
    if db.query(SearchMetrics).filter(SearchMetrics.brand_id == brand.id).count() == 0:
        now = datetime.utcnow()
        queries = [
            ("ai marketing agent", "/", 42, 650, 0.065, 3.2),
            ("autonomous cmo", "/product", 38, 520, 0.073, 2.8),
            ("standbharat vs hubspot", "/compare/hubspot", 29, 310, 0.093, 1.9),
            ("marketing automation operating system", "/", 21, 480, 0.044, 4.5)
        ]
        for days_ago in range(14):
            day_date = now - timedelta(days=days_ago)
            for q, p, clicks, imps, ctr, pos in queries:
                db.add(SearchMetrics(
                    id=uuid.uuid4(),
                    workspace_id=ws.id,
                    brand_id=brand.id,
                    date=day_date,
                    query=q,
                    page=p,
                    clicks=clicks,
                    impressions=imps,
                    ctr=ctr,
                    position=pos
                ))

    # Ensure Activity Events
    if db.query(ActivityEvent).filter(ActivityEvent.brand_id == brand.id).count() == 0:
        events = [
            ActivityEvent(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                type="SYSTEM_INITIALIZED",
                description="StandBharat autonomous multi-agent operating system initialized for StandBharat Global.",
                metadata_json={"tier": "enterprise", "agents_registered": 15}
            ),
            ActivityEvent(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                type="BRAND_BRAIN_VERIFIED",
                description="Brand Voice, Positioning, and Competitor Intelligence loaded into unified Brand Brain.",
                metadata_json={"voice": "Visionary & Authoritative", "competitors_tracked": 3}
            ),
            ActivityEvent(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                type="CAMPAIGN_ACTIVATED",
                description="Active campaign 'Q4 AI CMO Enterprise Launch' active across organic search and social.",
                metadata_json={"campaign_name": "Q4 AI CMO Enterprise Launch"}
            )
        ]
        for ev in events:
            db.add(ev)

    # Ensure Initial Content Project & Brief
    if db.query(ContentProject).filter(ContentProject.brand_id == brand.id).count() == 0:
        cp = ContentProject(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            brand_id=brand.id,
            title="Why Modern Growth Teams Need an Autonomous AI CMO",
            content_type="BLOG_POST",
            status="IN_PROGRESS"
        )
        db.add(cp)
        db.commit()
        db.refresh(cp)

        cb = ContentBrief(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            brand_id=brand.id,
            content_project_id=cp.id,
            title="Why Modern Growth Teams Need an Autonomous AI CMO",
            content_type="BLOG_POST",
            objective="Establish authority in agentic marketing and drive workspace signups.",
            target_audience="High-growth Founders and Enterprise CMOs",
            key_message="StandBharat replaces agency bloat with continuous autonomous execution.",
            tone="Visionary & Authoritative",
            call_to_action="Launch your autonomous marketing workspace today.",
            keywords="ai cmo, marketing automation, agentic marketing"
        )
        db.add(cb)
        db.commit()
        db.refresh(cb)

        cd = ContentDraft(
            id=uuid.uuid4(),
            workspace_id=ws.id,
            brand_id=brand.id,
            content_project_id=cp.id,
            brief_id=cb.id,
            title="The Shift to Autonomous Marketing Operating Systems",
            status="PENDING_REVIEW"
        )
        db.add(cd)
        db.commit()
        db.refresh(cd)

        cv = ContentVersion(
            id=uuid.uuid4(),
            content_draft_id=cd.id,
            version_number=1,
            title=cd.title,
            body="# The Shift to Autonomous Marketing Operating Systems\n\nMarketing is experiencing an architectural paradigm shift...",
            change_summary="Initial draft synthesized by Content Writer Agent.",
            created_by=str(user.id)
        )
        db.add(cv)

    # Ensure Publication
    if db.query(Publication).filter(Publication.brand_id == brand.id).count() == 0:
        draft = db.query(ContentDraft).filter(ContentDraft.brand_id == brand.id).first()
        if draft:
            pub = Publication(
                id=uuid.uuid4(),
                workspace_id=ws.id,
                brand_id=brand.id,
                content_project_id=draft.content_project_id,
                content_draft_id=draft.id,
                platform="linkedin",
                status="SCHEDULED",
                scheduled_for=datetime.utcnow() + timedelta(days=2),
                idempotency_key=f"pub_{draft.id}_linkedin",
                created_by=user.id
            )
            db.add(pub)

    db.commit()
    logger.info("Demo user, workspace, brand, and comprehensive data seeding verified.")
    return user
