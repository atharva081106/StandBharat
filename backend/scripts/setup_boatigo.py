import asyncio
import uuid
import datetime
from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.all_models import (
    User, Workspace, WorkspaceMember, Brand, BrandVoice, Audience, Competitor,
    WebsiteAnalysis, Integration, TrafficMetrics, SearchMetrics,
    ContentProject, ContentDraft, ContentApproval, AgentRun
)
from app.services.website_analysis import WebsiteAnalysisService

async def setup():
    db = SessionLocal()
    try:
        # 1. User
        email = "somyajain1205@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                hashed_password=get_password_hash("password123"),
                name="somya"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {user.email} ({user.id})")
        else:
            print(f"Existing user: {user.email} ({user.id})")

        # 2. Workspace
        workspace = db.query(Workspace).filter(Workspace.name == "boatigo").first()
        if not workspace:
            workspace = Workspace(
                name="boatigo",
                slug="boatigo",
                owner_id=user.id
            )
            db.add(workspace)
            db.commit()
            db.refresh(workspace)
            print(f"Created workspace: {workspace.name} ({workspace.id})")
        else:
            print(f"Existing workspace: {workspace.name} ({workspace.id})")

        # Member
        member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace.id,
            WorkspaceMember.user_id == user.id
        ).first()
        if not member:
            member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=user.id,
                role="OWNER"
            )
            db.add(member)
            db.commit()

        # 3. Brand
        brand = db.query(Brand).filter(
            Brand.workspace_id == workspace.id,
            Brand.name == "boatigo"
        ).first()
        if not brand:
            brand = Brand(
                workspace_id=workspace.id,
                name="boatigo",
                website_url="https://boatigo.in/",
                industry="Travel & Tourism",
                category="Experiential Travel",
                location="India",
                mission="India's first unified digital platform for experiences. Discover, book, and create unforgettable moments.",
                vision="To become Bharat's premier gateway to offbeat, authentic local culture and adventures.",
                tagline="Discover India Through Experiences",
                status="ACTIVE"
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)
            print(f"Created brand: {brand.name} ({brand.id})")
        else:
            brand.website_url = "https://boatigo.in/"
            brand.status = "ACTIVE"
            db.commit()

        # 4. Brand Voice
        voice = db.query(BrandVoice).filter(BrandVoice.brand_id == brand.id).first()
        if not voice:
            voice = BrandVoice(
                brand_id=brand.id,
                tone="Inspiring, adventurous, authentic, culturally grounded, inviting",
                personality="The Expert Local Explorer",
                writing_style="Narrative, evocative, crisp, authoritative yet warm",
                preferred_language="English, Hindi, Hinglish",
                formality="Semi-formal / Conversational",
                humor="Subtle, witty, relatable",
                words_to_use="Discover, authentic, immersive, untold, indigenous, moments, unforgettable, Bharat",
                words_to_avoid="Cheap, bargain, generic, touristy, bucket-list hack",
                messaging_rules="Always champion verified local community guides and zero-trace travel."
            )
            db.add(voice)

        # 5. Audience
        audience = db.query(Audience).filter(Audience.brand_id == brand.id).first()
        if not audience:
            audience = Audience(
                brand_id=brand.id,
                name="Urban Explorers & Weekend Travelers",
                description="Young professionals and adventurous couples (aged 24-38) residing in tech hubs (Bengaluru, Mumbai, Pune, Delhi NCR) seeking immersive weekend escapes.",
                pain_points="Generic crowded tourist traps, unverified operators, lack of authentic regional storytelling",
                preferred_channels="Instagram, LinkedIn, Organic Search, Travel Subreddits"
            )
            db.add(audience)

        # 6. Competitors
        comp_names = [
            ("Thrillophilia", "https://thrillophilia.com", "High-volume adventure tours, but cluttered marketplace and lacks curated bespoke experiences."),
            ("Klook", "https://klook.com", "Global ticketing platform, lacks deep Bharat localization and Tier-2/3 offbeat experiences."),
            ("MakeMyTrip", "https://makemytrip.com", "Mass market flights & hotels aggregator; experiences are an afterthought.")
        ]
        for name, web, desc in comp_names:
            c = db.query(Competitor).filter(Competitor.brand_id == brand.id, Competitor.name == name).first()
            if not c:
                c = Competitor(
                    brand_id=brand.id,
                    name=name,
                    website=web,
                    description=desc
                )
                db.add(c)

        # 7. Website Analysis
        analysis = db.query(WebsiteAnalysis).filter(WebsiteAnalysis.brand_id == brand.id).first()
        if not analysis:
            analysis = WebsiteAnalysis(
                brand_id=brand.id,
                workspace_id=workspace.id,
                url=brand.website_url
            )
            db.add(analysis)

        analysis.status = "COMPLETED"
        analysis.result_metadata = {
            'final_url': 'https://boatigo.in/',
            'http_status': 200,
            'https': True,
            'title': 'BoaTiGo — Discover India Through Experiences',
            'title_length': 44,
            'meta_description': "India's first unified digital platform for Experiences. Discover, book, and create unforgettable moments.",
            'meta_description_exists': True,
            'canonical_exists': True,
            'canonical_url': 'https://boatigo.in',
            'h1_count': 1,
            'h1_exists': True,
            'h1_first': 'Discover IndiaThrough Experiences',
            'h2_count': 12,
            'open_graph_exists': True,
            'language': 'en',
            'word_count': 592,
            'internal_links': 4,
            'external_links': 6,
            'image_count': 2,
            'images_missing_alt': 1,
            'robots_exists': True,
            'sitemap_exists': True
        }
        analysis.analysis_results = {
            'core_offering': 'Experiential travel booking & curation platform in India',
            'primary_theme': 'Offbeat adventures, heritage trails, scuba diving, and community treks',
            'seo_score': 92
        }

        # 8. Integrations (GA4 & GSC)
        for provider in ['ga4', 'gsc']:
            integ = db.query(Integration).filter(
                Integration.brand_id == brand.id,
                Integration.provider == provider
            ).first()
            if not integ:
                integ = Integration(
                    brand_id=brand.id,
                    workspace_id=workspace.id,
                    provider=provider,
                    status='CONNECTED',
                    last_sync_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=12)
                )
                db.add(integ)
            else:
                integ.status = 'CONNECTED'
                integ.last_sync_at = datetime.datetime.utcnow() - datetime.timedelta(minutes=12)

        # 9. TrafficMetrics
        db.query(TrafficMetrics).filter(TrafficMetrics.brand_id == brand.id).delete()
        base_date = datetime.datetime.utcnow()
        sources = [
            ('google', 'organic', '/', 620, 540, 2100, 0.68, 24),
            ('direct', '(none)', '/', 380, 310, 1200, 0.58, 12),
            ('linkedin', 'social', '/experiences', 240, 210, 890, 0.72, 8),
            ('instagram', 'social', '/experiences/goa-scuba', 180, 160, 700, 0.61, 4)
        ]
        for src, med, lp, sess, users, pv, eng, conv in sources:
            tm = TrafficMetrics(
                workspace_id=workspace.id,
                brand_id=brand.id,
                date=base_date - datetime.timedelta(days=1),
                source=src,
                medium=med,
                landing_page=lp,
                sessions=sess,
                active_users=users,
                pageviews=pv,
                engagement_rate=eng,
                conversions=conv
            )
            db.add(tm)

        # 10. SearchMetrics
        db.query(SearchMetrics).filter(SearchMetrics.brand_id == brand.id).delete()
        queries = [
            ('experiential travel india', '/', 142, 3200, 0.044, 8.2),
            ('boatigo', '/', 88, 1400, 0.063, 1.2),
            ('unique travel experiences india', '/experiences', 54, 2100, 0.026, 12.4),
            ('hidden treks western ghats', '/experiences/western-ghats', 28, 1720, 0.016, 16.8)
        ]
        for q, p, clicks, imp, ctr, pos in queries:
            sm = SearchMetrics(
                workspace_id=workspace.id,
                brand_id=brand.id,
                date=base_date - datetime.timedelta(days=1),
                query=q,
                page=p,
                clicks=clicks,
                impressions=imp,
                ctr=ctr,
                position=pos
            )
            db.add(sm)

        # 11. Approvals and Content Drafts (3 pending)
        db.query(ContentApproval).filter(ContentApproval.brand_id == brand.id).delete()
        db.query(ContentDraft).filter(ContentDraft.brand_id == brand.id).delete()
        db.query(ContentProject).filter(ContentProject.brand_id == brand.id).delete()

        posts_data = [
            {
                'title': 'Why Experiential Travel is Replacing Sightseeing in India (2026 Trends)',
                'type': 'linkedin_post',
                'body': 'Travel used to be about the selfie in front of the monument.\n\nIn 2026, Indian travelers are demanding something deeper: immersive local experiences, culinary trails, and hidden adventures.\n\nAt BoaTiGo, we are unifying experience curation across Bharat so explorers discover what guides never put in the brochures.\n\nWhat was the most transformative local experience you had in India this year? #ExperientialTravel #BoaTiGo #DiscoverBharat'
            },
            {
                'title': 'Top 5 Hidden Waterfall Treks in the Western Ghats for Weekend Explorers',
                'type': 'article',
                'body': 'Escaping the city bustle does not require a week-long expedition. The Western Ghats house some of India\'s most pristine, untouched waterfalls within a 4-hour drive of major hubs.\n\n1. Devkund Secret Falls\n2. Kataldhar Canyon Plunge\n3. Jogigundi Emerald Pool\n4. Shivagange Ravine\n5. Chelavara Hidden Cascade\n\nTips before you go: Respect local indigenous trails, carry zero plastic, and book licensed local community guides via BoaTiGo.'
            },
            {
                'title': 'The Ultimate Guide to Scuba Diving in the Andamans: Beyond Havelock',
                'type': 'seo_blog',
                'body': 'Crystal clear coral gardens, manta ray sanctuaries, and historical shipwrecks.\n\nWhile most tourists crowd Elephant Beach, certified divers know the real magic lies at Dixon\'s Pinnacle and Johnny\'s Gorge in the Ritchie\'s Archipelago.\n\nHere is everything you need to know about seasonality, certification levels (PADI vs SSI), and sustainable diving practices in the Andaman Sea.'
            }
        ]

        for item in posts_data:
            proj = ContentProject(
                workspace_id=workspace.id,
                brand_id=brand.id,
                title=item['title'],
                content_type=item['type'],
                status='IN_REVIEW',
                created_by=user.id
            )
            db.add(proj)
            db.flush()

            draft = ContentDraft(
                content_project_id=proj.id,
                workspace_id=workspace.id,
                brand_id=brand.id,
                title=item['title'],
                content_type=item['type'],
                body=item['body'],
                status='IN_REVIEW',
                generated_by='content_writer_agent'
            )
            db.add(draft)
            db.flush()

            approval = ContentApproval(
                content_project_id=proj.id,
                content_draft_id=draft.id,
                workspace_id=workspace.id,
                brand_id=brand.id,
                requested_by=user.id,
                status='PENDING'
            )
            db.add(approval)

        # 12. Agent Runs
        db.query(AgentRun).filter(AgentRun.brand_id == brand.id).delete()
        runs_data = [
            ('writer', 'SUCCESS', {'summary': 'Generated 3 high-impact drafts for review'}),
            ('competitor', 'SUCCESS', {'summary': 'Benchmarked positioning vs Thrillophilia and Klook'}),
            ('seo', 'SUCCESS', {'summary': 'Audited on-page metadata and internal link distribution'}),
            ('geo', 'SUCCESS', {'summary': 'Analyzed Perplexity & ChatGPT citation share for brand terms'})
        ]
        for aid, st, out in runs_data:
            ar = AgentRun(
                workspace_id=workspace.id,
                brand_id=brand.id,
                agent_id=aid,
                status=st,
                output=out,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
            )
            db.add(ar)

        db.commit()
        print("Setup completed successfully for boatigo!")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(setup())
