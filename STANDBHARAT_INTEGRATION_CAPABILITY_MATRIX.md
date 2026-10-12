# StandBharat Integration Capability Matrix

| Provider | Connection Method | Required Permissions / App | Account Types | Read / Auth | Publishing | Media Support | Available Metrics | Token Refresh | Current Status | Verification | Remaining Blockers |
|----------|-------------------|----------------------------|---------------|-------------|------------|---------------|-------------------|---------------|----------------|--------------|--------------------|
| **GA4** | OAuth 2.0 | `analytics.readonly` | Google | Yes | No | N/A | Sessions, Users, Conversions | Yes | IMPLEMENTED | VERIFIED LIVE | None |
| **GSC** | OAuth 2.0 | `webmasters.readonly` | Google | Yes | No | N/A | Impressions, Clicks, CTR, Pos | Yes | IMPLEMENTED | VERIFIED LIVE | None |
| **WordPress** | App Password | REST API Access | Any WP | Yes | Yes (Posts) | Handled externally | None | N/A | IMPLEMENTED | VERIFIED LIVE | None |
| **LinkedIn** | OAuth 2.0 | `w_member_social`, `r_liteprofile` | Personal/Org | Yes (URN) | Yes (Text) | None yet | None (Gated) | Yes | IMPLEMENTED | VERIFIED LIVE | Metrics require enterprise MDP access. Media upload requires additional endpoints. |
| **X (Twitter)**| OAuth 2.0 (PKCE) | `tweet.read`, `tweet.write`, `users.read` | Personal | Yes | Yes (Text) | None yet | None yet | Yes | STUBBED | BLOCKED | Needs implementation and X API credentials. |
| **Reddit** | OAuth 2.0 | `read`, `submit`, `identity` | Personal | Yes | Yes (Text/Link)| None yet | Upvotes/Comments | Yes | STUBBED | BLOCKED | Needs implementation and Reddit App credentials. |
| **Instagram**| OAuth 2.0 | `instagram_basic`, `instagram_content_publish` | Professional/Creator | Yes | Yes (Image/Reel)| Images/Video | Reach, Engagement | Yes | NOT IMPLEMENTED| BLOCKED | Meta Graph API credentials. |
| **Facebook Pages** | OAuth 2.0 | `pages_manage_posts`, `pages_read_engagement` | Pages | Yes | Yes (Post) | Image/Video | Impressions, Reach| Yes | NOT IMPLEMENTED| BLOCKED | Meta Graph API credentials. |
| **YouTube** | OAuth 2.0 | `youtube.upload`, `youtube.readonly` | Channel | Yes | Yes (Video)| Video | Views, Watch Time | Yes | NOT IMPLEMENTED| BLOCKED | Google API YouTube Data access. |
| **TikTok** | OAuth 2.0 | `video.upload`, `user.info.basic` | Any | Yes | Yes (Video)| Video | Views, Likes | Yes | NOT IMPLEMENTED| BLOCKED | TikTok for Developers credentials. |
