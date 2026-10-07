import { BrandBrainProvider } from '../types/interfaces';

export class MockBrandBrainProvider implements BrandBrainProvider {
  private context = {
    brand: {
      name: "StandBharat AI",
      description: "An AI-powered autonomous marketing operating system for enterprise B2B.",
      industry: "B2B SaaS",
      category: "Marketing Automation",
      website_url: "https://standbharat.ai",
      mission: "To automate the intelligence loop from data to publishing.",
      vision: "Be the operating system for the next generation of marketers.",
      values: "Data-driven, Autonomous, Premium",
      tagline: "Your Autonomous Marketing Team"
    },
    voice: {
      tone: "Professional yet approachable, authoritative on AI.",
      personality: "Intelligent, calm, operational, and trustworthy.",
      writing_style: "Concise, data-backed, avoiding hype-words.",
      preferred_language: "US English"
    },
    audiences: [
      { id: "1", name: "CMOs", description: "Chief Marketing Officers at mid-to-large enterprises", pain_points: "Attribution, tool fatigue, scaling content" },
      { id: "2", name: "Growth Leads", description: "Technical marketers focused on revenue", pain_points: "Experimentation speed, data silos" }
    ],
    products: [
      { id: "1", name: "StandBharat Platform", description: "The core AI marketing OS", price: "$999/mo" }
    ],
    positioning: {
      positioning_statement: "For enterprise marketing teams, StandBharat is the only AI operating system that completely closes the loop from analytics to publishing without human bottlenecks."
    },
    goals: [
      { id: "1", goal: "Increase Demo Requests", target_value: "500/mo", current_value: "320/mo" }
    ],
    competitors: [
      { id: "1", name: "Legacy Automation Co", strengths: "Enterprise features, established integrations", weaknesses: "Clunky UI, no native AI intelligence" },
      { id: "2", name: "AI Wrapper Inc", strengths: "Fast onboarding", weaknesses: "No data loop, just generates generic copy" }
    ],
    strategy: {
      marketing_strategy: "Content-led growth focusing on deep-dive technical guides and thought leadership on LinkedIn."
    },
    documents: []
  };

  async getContext() {
    return this.context;
  }
  async updateVoice(data: any) {
    this.context.voice = { ...this.context.voice, ...data };
    return this.context.voice;
  }
  async addAudience(data: any) {
    const aud = { id: Math.random().toString(), ...data };
    this.context.audiences.push(aud);
    return aud;
  }
  async updateAudience(id: string, data: any) {
    return data;
  }
  async deleteAudience(id: string) {
    this.context.audiences = this.context.audiences.filter(a => a.id !== id);
    return { status: "ok" };
  }
  async addProduct(data: any) {
    const prod = { id: Math.random().toString(), ...data };
    this.context.products.push(prod);
    return prod;
  }
  async updateProduct(id: string, data: any) {
    return data;
  }
  async deleteProduct(id: string) {
    this.context.products = this.context.products.filter(p => p.id !== id);
    return { status: "ok" };
  }
  async updatePositioning(data: any) {
    this.context.positioning = { ...this.context.positioning, ...data };
    return this.context.positioning;
  }
  async addGoal(data: any) {
    const goal = { id: Math.random().toString(), ...data };
    this.context.goals.push(goal);
    return goal;
  }
  async updateGoal(id: string, data: any) {
    return data;
  }
  async deleteGoal(id: string) {
    this.context.goals = this.context.goals.filter(g => g.id !== id);
    return { status: "ok" };
  }
  async addCompetitor(data: any) {
    const comp = { id: Math.random().toString(), ...data };
    this.context.competitors.push(comp);
    return comp;
  }
  async updateCompetitor(id: string, data: any) {
    return data;
  }
  async deleteCompetitor(id: string) {
    this.context.competitors = this.context.competitors.filter(c => c.id !== id);
    return { status: "ok" };
  }
  async updateStrategy(data: any) {
    this.context.strategy = { ...this.context.strategy, ...data };
    return this.context.strategy;
  }
}
