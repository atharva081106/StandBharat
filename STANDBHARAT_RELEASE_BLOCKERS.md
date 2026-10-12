# StandBharat Release Blockers & Prioritized Remediation

## 1. Identified Defects & Remediation Log

### P0 (Critical Security & Core Integrity)
- **None Detected**: Cross-tenant data isolation, credential encryption, OAuth CSRF state checking, and manual approval safeguards are fully operational.

### P1 (Core Product Loop Failures)
- **Defect**: Missing true back-reference key between `Opportunity` and `Publication`. Currently the learning loop relies on implicit timestamps.
- **Remediation**: Feasible for immediate next patch. Needs an explicit `opportunity_id` passed through the Content Drafting schema into the final Publication table.

### P2 (Major Missing Capabilities)
- **Defect**: Social API scopes missing.
- **Remediation (BLOCKED)**: 
  - **Meta (Facebook/Instagram)**: Requires passing App Review for `pages_read_engagement` and `instagram_manage_insights`.
  - **LinkedIn**: Requires upgrading developer app to Enterprise tier or being allowlisted for the `r_organization_social` API.
  - **X (Twitter) & Reddit**: Missing valid API keys for production.
- **Defect**: No clear revenue attribution from CRM.
- **Remediation**: Safe to pilot as long as user is aware ROI metrics rely solely on GA4 eCommerce conversion payloads. 

### P3 (Minor UX & Test Maintenance)
- **Defect**: Pytest suite failing on 5 tests mostly due to Pydantic V1/V2 syntax deprecations in models.
- **Remediation**: Needs a minor ticket to migrate schema configs from `class Config:` to `model_config = ConfigDict()`.

## 2. Release Recommendation

**DECISION: READY FOR CONTROLLED PILOT**

**Conditions & Justification:**
1. **Security & Scope Boundaries**: The application has proven its ability to sandbox data properly per Workspace and Brand.
2. **Execution Safety**: The AI agents write to databases; they do *not* execute spontaneous physical external actions without explicit `Approved` flags.
3. **Missing Features are Handled Gracefully**: Integrations that lack scopes or analytics return standard `UNAVAILABLE` or `MOCKED` flags rather than crashing the system or displaying hallucinatory metrics.

The platform is safe to be piloted with real users assuming they are manually onboarding their own GSC/GA4 accounts and are comfortable knowing some rich social analytics may be delayed until full App Review passes.
