# StandBharat Attribution & Performance Capability Matrix

| Provider | Sync Capabilities | Attribution Capabilities | Live Verification Status | Missing / Blocked Permissions |
|----------|-------------------|--------------------------|--------------------------|-------------------------------|
| **Google Analytics 4 (GA4)** | `TrafficMetrics`: Sessions, Views, Conversions, Engagement Rate by `source`, `medium`, `campaign`. | **HIGH**: Can parse standard UTM tags mapped to social campaigns and external posts. | VERIFIED LIVE | None |
| **Google Search Console (GSC)** | `SearchMetrics`: Clicks, Impressions, CTR, Position by `query`, `page`. | **MEDIUM**: Page-level SEO attribution; cannot tie directly to a specific social push reliably. | VERIFIED LIVE | None |
| **LinkedIn** | `PerformanceSnapshot`: Impressions, Clicks, Likes, Comments, Shares. | **LOW**: LinkedIn restricts detailed socialActions and share statistics for personal profiles without enterprise organization scopes. | MOCKED | Missing `r_organization_social` and `rw_organization_admin` for full UGC metrics. |
| **X (Twitter)** | `PerformanceSnapshot`: Likes, Reposts, Replies, Impressions. | **MEDIUM**: Can fetch v2 tweet metrics if `tweet.read` is fully authorized. | MOCKED | Requires Pro API tier for reliable historic lookup. |
| **Reddit** | `PerformanceSnapshot`: Upvotes, Comments. | **LOW**: Upvotes and comments available, but no reliable view/impression count for 3rd-party devs. | MOCKED | API limits impression data visibility. |
| **Facebook Pages** | `PerformanceSnapshot`: Reach, Engagement, Reactions, Clicks. | **HIGH**: Graph API returns accurate post insights. | BLOCKED | Requires `pages_read_engagement` App Review. |
| **Instagram** | `PerformanceSnapshot`: Reach, Likes, Comments, Saves. | **HIGH**: Graph API returns accurate media insights. | BLOCKED | Requires `instagram_manage_insights` App Review. |
| **YouTube** | `PerformanceSnapshot`: Views, Likes, Comments. | **MEDIUM**: YouTube Data API v3 provides basic video statistics. | BLOCKED | Requires `youtube.readonly` scope. |
| **TikTok** | `PerformanceSnapshot`: Views, Likes, Shares, Comments. | **MEDIUM**: TikTok API provides basic video statistics. | BLOCKED | Requires TikTok Developer approval. |

## Attribution Methodology
- **Observed Conversions**: Direct `conversions` reported by GA4 for a specific `landing_page` and `campaign`.
- **Attributed Conversions**: Conversions matching a `campaign` UTM tag that corresponds to a StandBharat `ContentProject` or `Publication`.
- **Estimated Impact**: For channels where UTMs are stripped or unavailable (e.g., direct dark social), StandBharat avoids fabricating attribution and marks it as `UNAVAILABLE`.

## Data Sufficiency Rules
- Revenue and CPA are only calculated if the `conversions` value from GA4 includes `currency` and `value` payloads. 
- If a post has less than 100 impressions or the data is older than 30 days without updates, the system flags it as `STALE_OR_INSUFFICIENT` to prevent hallucinated recommendations.
