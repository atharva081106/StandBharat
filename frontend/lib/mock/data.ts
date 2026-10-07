export const DEMO_MODE = true;

export const mockUser = {
  id: "u_1",
  name: "Atharva",
  email: "demo@standbharat.ai",
  role: "OWNER"
};

export const mockWorkspaces = [
  { id: "w_1", name: "Acme Corp" }
];

export const mockBrands = [
  { id: "b_1", name: "Acme SaaS", workspace_id: "w_1" }
];

export const mockKPIs = {
  revenue: { value: "₹4.82L", change: "+18.4%" },
  leads: { value: "1,284", change: "+23.1%" },
  conversionRate: { value: "8.4%", change: "+2.1%" },
  aiSpend: { value: "₹2,410", change: "+8.2%" }
};

export const mockAgents = [
  { id: "analytics", name: "Analytics Agent", status: "ACTIVE", description: "Monitors performance metrics and ingests analytics data.", capabilities: ["Data Ingestion", "Metric Tracking", "Trend Analysis"] },
  { id: "competitor", name: "Competitor Agent", status: "ACTIVE", description: "Tracks competitor positioning, pricing, and content gaps.", capabilities: ["Market Scanning", "Gap Analysis", "Competitor Profiling"] },
  { id: "growth", name: "Growth Agent", status: "ACTIVE", description: "Identifies growth opportunities and formulates strategic hypotheses.", capabilities: ["Opportunity Scoring", "Hypothesis Generation", "Revenue Modeling"] },
  { id: "content_strategy", name: "Content Strategy Agent", status: "ACTIVE", description: "Translates opportunities into actionable content briefs.", capabilities: ["Brief Generation", "SEO Outlining", "Content Planning"] },
  { id: "content_writer", name: "Content Writer Agent", status: "WAITING", description: "Drafts high-quality content based on approved briefs.", capabilities: ["Long-form Writing", "Copywriting", "Tone Matching"] },
  { id: "content_publisher", name: "Content Publisher Agent", status: "IDLE", description: "Deploys approved content to external platforms (e.g. LinkedIn).", capabilities: ["API Integration", "Scheduling", "Cross-posting"] }
];

export const mockOpportunities = [
  { id: "o_1", title: "Target enterprise keyword 'AI Marketing Automation'", impact: "HIGH", confidence: "87%", effort: "MEDIUM", priority: 8.6, status: "NEW" },
  { id: "o_2", title: "Counter competitor X's new pricing model", impact: "HIGH", confidence: "92%", effort: "HIGH", priority: 8.2, status: "IN_PROGRESS" },
  { id: "o_3", title: "Launch LinkedIn series on predictive analytics", impact: "MEDIUM", confidence: "75%", effort: "LOW", priority: 7.0, status: "COMPLETED" }
];

export const mockApprovals = [
  { id: "a_1", title: "Review Content Brief: Enterprise AI Marketing", agent: "Content Strategy Agent", risk: "LOW", requested: "2 hours ago" },
  { id: "a_2", title: "Approve LinkedIn Draft: Predictive Analytics Post 1", agent: "Content Writer Agent", risk: "MEDIUM", requested: "5 hours ago" }
];

export const mockContent = [
  { id: "c_1", title: "Enterprise AI Marketing Automation Guide", type: "Blog", status: "DRAFT", author: "Content Writer Agent", updated: "1 hour ago" },
  { id: "c_2", title: "Predictive Analytics Post 1", type: "LinkedIn Post", status: "PUBLISHED", author: "Content Publisher Agent", updated: "1 day ago" },
  { id: "c_3", title: "Competitor X Feature Comparison", type: "Battlecard", status: "IN_REVIEW", author: "Content Strategy Agent", updated: "3 hours ago" }
];

export const mockRecentActivity = [
  { id: "act_1", type: "Generated", description: "Draft 'Enterprise AI Marketing Guide'", agent: "Content Writer Agent" },
  { id: "act_2", type: "Identified", description: "New keyword opportunity 'AI Marketing'", agent: "Growth Agent" },
  { id: "act_3", type: "Analyzed", description: "Competitor X pricing update", agent: "Competitor Agent" },
  { id: "act_4", type: "Ingested", description: "Weekly analytics payload", agent: "Analytics Agent" }
];
