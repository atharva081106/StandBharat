import socket
import urllib.parse
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import traceback
import json
from app.ai.gateway import ai_gateway
from app.ai.schemas import AIRequestMessage
from app.ai.exceptions import AINotConfiguredException

class SSRFProtectionError(Exception):
    pass

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
            
        hostname = parsed.hostname
        if not hostname:
            return False
            
        # Basic localhost/internal checks
        if hostname in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            return False
            
        # Resolve IP to block internal ranges
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            return False
            
        parts = ip.split('.')
        if len(parts) == 4:
            # 10.x.x.x
            if parts[0] == '10':
                return False
            # 172.16.x.x - 172.31.x.x
            if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
                return False
            # 192.168.x.x
            if parts[0] == '192' and parts[1] == '168':
                return False
            # 169.254.x.x (link-local)
            if parts[0] == '169' and parts[1] == '254':
                return False
                
        return True
    except Exception:
        return False

class WebsiteAnalysisService:
    @staticmethod
    async def analyze_url(url: str) -> dict:
        if not url.startswith('http'):
            url = 'https://' + url
            
        if not is_safe_url(url):
            raise SSRFProtectionError("Invalid or unsafe URL provided.")
            
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(url)
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Basic Extracted SEO
            title = soup.title.string.strip() if soup.title and soup.title.string else None
            
            meta_desc = None
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag and desc_tag.get('content'):
                meta_desc = desc_tag.get('content')
                
            canonical = None
            canon_tag = soup.find('link', rel='canonical')
            if canon_tag and canon_tag.get('href'):
                canonical = canon_tag.get('href')
                
            h1_tags = [h.get_text(strip=True) for h in soup.find_all('h1')]
            h2_tags = [h.get_text(strip=True) for h in soup.find_all('h2')]
            
            # Images
            images = soup.find_all('img')
            images_missing_alt = sum(1 for img in images if not img.get('alt'))
            
            # Open Graph
            og_title = None
            og_tag = soup.find('meta', property='og:title')
            if og_tag:
                og_title = og_tag.get('content')
                
            og_image = None
            og_img_tag = soup.find('meta', property='og:image')
            if og_img_tag:
                og_image = og_img_tag.get('content')

            # Language
            lang = None
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                lang = html_tag.get('lang')
                
            # Links
            internal_links = 0
            external_links = 0
            base_domain = urlparse(str(response.url)).netloc
            
            for a in soup.find_all('a', href=True):
                href = a.get('href')
                if href.startswith('http'):
                    if urlparse(href).netloc == base_domain:
                        internal_links += 1
                    else:
                        external_links += 1
                elif href.startswith('/'):
                    internal_links += 1

            word_count = len(soup.get_text(separator=' ', strip=True).split())

            metadata = {
                "final_url": str(response.url),
                "http_status": response.status_code,
                "https": str(response.url).startswith('https'),
                "title": title,
                "title_length": len(title) if title else 0,
                "meta_description": meta_desc,
                "meta_description_exists": bool(meta_desc),
                "canonical_exists": bool(canonical),
                "canonical_url": canonical,
                "h1_count": len(h1_tags),
                "h1_exists": len(h1_tags) > 0,
                "h1_first": h1_tags[0] if h1_tags else None,
                "h2_count": len(h2_tags),
                "open_graph_exists": bool(og_title or og_image),
                "language": lang,
                "word_count": word_count,
                "internal_links": internal_links,
                "external_links": external_links,
                "image_count": len(images),
                "images_missing_alt": images_missing_alt,
            }

            # In a real app, we'd do a secondary fetch for robots.txt and sitemap.xml
            # For simplicity we'll just attempt a quick HEAD request.
            robots_url = urllib.parse.urljoin(str(response.url), '/robots.txt')
            sitemap_url = urllib.parse.urljoin(str(response.url), '/sitemap.xml')
            
            try:
                async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
                    r_rob = await client.head(robots_url)
                    metadata["robots_exists"] = r_rob.status_code == 200
                    r_sit = await client.head(sitemap_url)
                    metadata["sitemap_exists"] = r_sit.status_code == 200
            except:
                metadata["robots_exists"] = False
                metadata["sitemap_exists"] = False

            text_content = soup.get_text(separator=' ', strip=True)
            truncated_text = text_content[:15000]

            analysis_results = {
                "description": None,
                "products_services": [],
                "target_audience": None,
                "value_proposition": None,
                "positioning": None,
                "brand_voice": None,
                "inferred_topics": []
            }

            try:
                ai_gateway._get_provider()
                prompt = f"""
                Analyze the following text extracted from a brand's website.
                
                Website Text:
                {truncated_text}
                
                Extract the following structured information about the brand:
                - "description": A concise company description.
                - "products_services": A list of products or services offered.
                - "target_audience": The primary target audience.
                - "value_proposition": The core value proposition.
                - "positioning": How the brand positions itself in the market.
                - "brand_voice": The tone and personality of the brand's writing.
                - "inferred_topics": A list of content topics relevant to the brand.
                
                Important: Do NOT invent facts. If the website text lacks evidence for a specific field, return null (for strings) or an empty list (for arrays).
                
                Return JSON strictly matching this schema:
                {{
                    "description": "string or null",
                    "products_services": ["string"],
                    "target_audience": "string or null",
                    "value_proposition": "string or null",
                    "positioning": "string or null",
                    "brand_voice": "string or null",
                    "inferred_topics": ["string"]
                }}
                """
                
                res = ai_gateway.generate(
                    messages=[
                        AIRequestMessage(role="system", content="You are a data extraction agent. You only extract facts explicitly present in the provided text. Output valid JSON only."),
                        AIRequestMessage(role="user", content=prompt)
                    ]
                )
                
                content = res.content.strip()
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                    
                parsed = json.loads(content.strip())
                analysis_results.update({
                    "description": parsed.get("description"),
                    "products_services": parsed.get("products_services", []),
                    "target_audience": parsed.get("target_audience"),
                    "value_proposition": parsed.get("value_proposition"),
                    "positioning": parsed.get("positioning"),
                    "brand_voice": parsed.get("brand_voice"),
                    "inferred_topics": parsed.get("inferred_topics", [])
                })
            except AINotConfiguredException:
                pass
            except Exception as e:
                print(f"AI extraction failed: {e}")

            return {
                "metadata": metadata,
                "analysis_results": analysis_results
            }
        except Exception as e:
            raise Exception(f"Failed to analyze website: {str(e)}\n{traceback.format_exc()}")
