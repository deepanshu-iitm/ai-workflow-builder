from serpapi import GoogleSearch
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings


class WebSearchService:
    """Service for performing web searches using SerpAPI."""
    
    def __init__(self):
        self.api_key = settings.SERPAPI_API_KEY
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        search_type: str = "google"
    ) -> Dict[str, Any]:
        """Perform a web search and return results."""
        if not self.api_key:
            return {
                "success": False,
                "error": "SerpAPI key not configured",
                "results": []
            }
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": search_type
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract organic results
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for result in organic_results[:num_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "query": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "query": query
            }
    
    def format_results_as_context(
        self,
        search_results: Dict[str, Any]
    ) -> str:
        """Format search results as context for LLM."""
        if not search_results.get("success") or not search_results.get("results"):
            return ""
        
        context_parts = ["Web Search Results:"]
        
        for i, result in enumerate(search_results["results"], 1):
            context_parts.append(
                f"\n{i}. {result['title']}\n"
                f"   URL: {result['link']}\n"
                f"   {result['snippet']}"
            )
        
        return "\n".join(context_parts)
    
    async def async_search(
        self,
        query: str,
        num_results: int = 5
    ) -> Dict[str, Any]:
        """Async version of web search using httpx."""
        if not self.api_key:
            return {
                "success": False,
                "error": "SerpAPI key not configured",
                "results": []
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": self.api_key,
                        "num": num_results,
                        "engine": "google"
                    },
                    timeout=30.0
                )
                
                results = response.json()
                
                organic_results = results.get("organic_results", [])
                
                formatted_results = []
                for result in organic_results[:num_results]:
                    formatted_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "position": result.get("position", 0)
                    })
                
                return {
                    "success": True,
                    "results": formatted_results,
                    "total_results": len(formatted_results),
                    "query": query
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "query": query
            }
