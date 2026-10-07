# Integration Architecture

## 1. Integration Abstraction
The system architecture must support external integrations via standardized abstractions, ensuring robust error handling, rate limiting, and observability. 

## 2. Initial Integration Categories
- **Analytics:** Google Analytics, Google Search Console
- **CMS:** WordPress, Webflow, Framer, Wix, Sanity
- **Development:** GitHub
- **Social:** LinkedIn, X, Reddit
- **Communication:** Slack, WhatsApp, Telegram
- **Storage:** S3-compatible storage
- **AI:** OpenAI, Anthropic, Gemini, Groq-compatible providers
- **Embedding:** Provider abstraction

## 3. Strict Safety & Realism Constraints
- The system must NEVER silently fake external API data, SEO rankings, AI search rankings, social publishing, Google Analytics, Search Console, OAuth, revenue, or campaign metrics.
- If an integration is unavailable, the system must return an explicit blocked/unavailable state.
- Never turn an unavailable external integration into fake success.

## 4. Competitor Intelligence Safety
External URL scraping and analysis must be protected against Server-Side Request Forgery (SSRF):
- HTTP/HTTPS only
- Timeout enforcement
- Redirect limits
- Response size limits
- Private IP blocking (No 10.0.0.0/8, 192.168.0.0/16, etc.)
- Localhost blocking
- Cloud metadata endpoint blocking
- DNS resolution validation prior to requesting
