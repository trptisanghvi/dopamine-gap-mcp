import httpx
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()
mcp = FastMCP("The Dopamine Gap")

PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
GUARDIAN_API_KEY = os.getenv("GUARDIAN_API_KEY")

@mcp.tool()
def search_clinical_literature(
    query: str,
    years_back: int = 10,
    max_results: int = 20
) -> str:
    """
    Search PubMed for peer-reviewed neuroscience research on a topic.
    Returns titles, publication years, journals, and abstracts.
    Use this to understand what clinical science actually says about a concept.
    """
    import datetime
    min_year = datetime.datetime.now().year - years_back

    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": f"{query}[Title/Abstract] AND {min_year}:{datetime.datetime.now().year}[PDAT]",
        "retmax": max_results,
        "api_key": PUBMED_API_KEY,
        "retmode": "json"
    }

    try:
        search_resp = httpx.get(search_url, params=search_params, timeout=15)
        ids = search_resp.json()["esearchresult"]["idlist"]

        if not ids:
            return f"No clinical literature found for '{query}' in the last {years_back} years."

        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids[:10]),
            "rettype": "abstract",
            "retmode": "text",
            "api_key": PUBMED_API_KEY
        }
        fetch_resp = httpx.get(fetch_url, params=fetch_params, timeout=15)
        return fetch_resp.text

    except Exception as e:
        return f"Error querying PubMed: {str(e)}"

@mcp.tool()
def search_public_discourse(
    query: str,
    from_year: int = 2012,
    max_results: int = 20
) -> str:
    """
    Search The Guardian's archive for public discourse around a concept.
    Returns headlines, publication dates, and article sections.
    Use this to understand how a scientific concept circulates in public language.
    Starting from 2012 captures the rise of wellness culture and social media discourse.
    """
    url = "https://content.guardianapis.com/search"
    params = {
        "q": query,
        "from-date": f"{from_year}-01-01",
        "order-by": "relevance",
        "show-fields": "headline,standfirst,bodyText",
        "page-size": max_results,
        "api-key": GUARDIAN_API_KEY
    }

    try:
        resp = httpx.get(url, params=params, timeout=15)
        data = resp.json()
        results = data["response"]["results"]

        if not results:
            return f"No public discourse found for '{query}' from {from_year} onwards."

        output = []
        for article in results[:10]:
            fields = article.get("fields", {})
            output.append(
                f"DATE: {article['webPublicationDate'][:10]}\n"
                f"HEADLINE: {fields.get('headline', 'N/A')}\n"
                f"STANDFIRST: {fields.get('standfirst', 'N/A')}\n"
                f"---"
            )
        return "\n".join(output)

    except Exception as e:
        return f"Error querying Guardian API: {str(e)}"

@mcp.tool()
def analyze_semantic_gap(
    clinical_term: str,
    public_term: str,
    concept_explanation: str = ""
) -> str:
    """
    The core tool. Queries both clinical literature and public discourse
    for related but distinct terms, then structures the comparison so Claude
    can analyze where and how the meaning has diverged.

    Example: clinical_term='dopamine reward prediction error'
             public_term='dopamine hit dopamine detox'
             concept_explanation='dopamine and motivation/reward'
    """
    clinical = search_clinical_literature(clinical_term, years_back=15)
    public = search_public_discourse(public_term, from_year=2010)

    return f"""
CLINICAL LITERATURE (PubMed):
Query: '{clinical_term}'
{clinical[:3000]}

---

PUBLIC DISCOURSE (The Guardian):
Query: '{public_term}'
{public[:3000]}

---

ANALYSIS PROMPT FOR CLAUDE:
Compare the clinical and public results above for the concept of '{concept_explanation or clinical_term}'.
Identify:
1. What specific claims does the clinical literature make?
2. What language and claims appear in public discourse?
3. Where is the gap largest — what does public discourse assert that clinical science does not support?
4. When did the divergence appear to accelerate?
5. What are the real-world consequences of this gap for mental health and public understanding?
"""
@mcp.tool()
def get_discourse_timeline(
    query: str,
    start_year: int = 2004,
    end_year: int = 2024
) -> str:
    """
    Queries The Guardian year by year for a term and returns article counts
    per year. This reveals when a concept entered or accelerated in public
    discourse — the data backbone for visualization.
    """
    timeline = {}

    for year in range(start_year, end_year + 1):
        url = "https://content.guardianapis.com/search"
        params = {
            "q": f'"{query}"' if ' ' in query else query,
            "from-date": f"{year}-01-01",
            "to-date": f"{year}-12-31",
            "api-key": GUARDIAN_API_KEY,
            "page-size": 1
        }
        try:
            resp = httpx.get(url, params=params, timeout=10)
            count = resp.json()["response"]["total"]
            timeline[year] = count
        except:
            timeline[year] = 0

    result = "DISCOURSE TIMELINE (articles per year):\n"
    for year, count in timeline.items():
        bar = "█" * min(count, 50)
        result += f"{year}: {bar} ({count})\n"

    return result
@mcp.tool()
def get_clinical_timeline(
    query: str,
    start_year: int = 2004,
    end_year: int = 2024
) -> str:
    """
    Queries PubMed year by year for a clinical term and returns
    paper counts per year — the clinical volume curve.
    """
    timeline = {}
    for year in range(start_year, end_year + 1):
        params = {
            "db": "pubmed",
            "term": f"{query}[Title/Abstract] AND {year}[PDAT]",
            "rettype": "count",
            "api_key": PUBMED_API_KEY,
            "retmode": "json"
        }
        try:
            resp = httpx.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params=params,
                timeout=10
            )
            count = int(resp.json()["esearchresult"]["count"])
            timeline[year] = count
        except:
            timeline[year] = 0

    result = "CLINICAL TIMELINE (papers per year):\n"
    for year, count in timeline.items():
        bar = "█" * min(count // 2, 50)
        result += f"{year}: {bar} ({count})\n"
    return result
@mcp.tool()
def get_clinical_ground_truth(concept: str) -> str:
    """
    Returns structured clinical ground-truth claims for a neuroscience
    concept, drawn from established peer-reviewed consensus. These are
    the specific claims public discourse should be evaluated against.
    """
    truths = {
        "dopamine": [
            "Dopamine signals reward prediction error — the difference between expected and received reward — not pleasure itself (Schultz et al., 1997)",
            "Dopamine operates in dual tonic/phasic systems across D1/D2 receptor circuits — not as discrete 'hits'",
            "There is no clinical evidence for a 'dopamine detox' mechanism — dopamine is a continuous neuromodulator",
            "Dopamine's role varies significantly by brain region — nucleus accumbens vs. prefrontal cortex vs. olfactory tubercle show distinct functions",
            "Wanting and liking are neurochemically dissociable — dopamine drives wanting/seeking, not hedonic pleasure (Berridge & Robinson)",
        ]
    }
    return "\n".join(truths.get(concept.lower(), ["No ground truth available for this concept."]))
if __name__ == "__main__":
    mcp.run()
