from app.schemas.brand_brain import BrandContextResponse

def build_brand_prompt_context(context: BrandContextResponse) -> str:
    prompt = f"Brand Name: {context.brand.name}\n"
    if context.brand.description:
        prompt += f"Description: {context.brand.description}\n"
        
    if context.voice:
        prompt += "\n## Brand Voice\n"
        prompt += f"- Tone: {context.voice.tone}\n" if context.voice.tone else ""
        prompt += f"- Personality: {context.voice.personality}\n" if context.voice.personality else ""
        prompt += f"- Target Language: {context.voice.preferred_language}\n" if context.voice.preferred_language else ""
        
    if context.positioning:
        prompt += "\n## Positioning\n"
        prompt += f"- Statement: {context.positioning.positioning_statement}\n" if context.positioning.positioning_statement else ""
        prompt += f"- UVP: {context.positioning.unique_value_proposition}\n" if context.positioning.unique_value_proposition else ""
        
    if context.audiences:
        prompt += "\n## Audiences\n"
        for aud in context.audiences:
            prompt += f"- {aud.name}: {aud.description}\n"
            
    if context.products:
        prompt += "\n## Products\n"
        for prod in context.products:
            prompt += f"- {prod.name}: {prod.description} ({prod.price})\n"
            
    if context.goals:
        prompt += "\n## Goals\n"
        for goal in context.goals:
            prompt += f"- {goal.goal} (Target: {goal.target_value}, Current: {goal.current_value})\n"
            
    if context.strategy:
        prompt += "\n## Strategy\n"
        prompt += f"- Business: {context.strategy.business_strategy}\n" if context.strategy.business_strategy else ""
        prompt += f"- Marketing: {context.strategy.marketing_strategy}\n" if context.strategy.marketing_strategy else ""
        
    return prompt.strip()
