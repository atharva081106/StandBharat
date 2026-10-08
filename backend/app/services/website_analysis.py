import socket
import urllib.parse
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import traceback

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

            return {
                "metadata": metadata,
                "analysis_results": {
                    "inferred_topics": ["Business", "Services"] if word_count > 50 else [],
                    "value_proposition": "Extracted value prop placeholder."
                }
            }
        except Exception as e:
            raise Exception(f"Failed to analyze website: {str(e)}\n{traceback.format_exc()}")
