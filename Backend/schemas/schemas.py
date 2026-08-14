from typing import Optional, Any
from pydantic import BaseModel, model_validator

class QueryRequest(BaseModel):
    query: Optional[str] = None
    prompt: Optional[str] = None
    message: Optional[str] = None
    text: Optional[str] = None
    name: Optional[str] = None
    answerType: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_query_fallback(cls, data: Any) -> Any:
        if isinstance(data, dict):
            q = data.get("query") or data.get("prompt") or data.get("message") or data.get("text") or ""
            data["query"] = q
        return data

# Alias for backwards compatibility
queryRequest = QueryRequest
"""
{
"query": "?"
}
"""
class PdfRequest(BaseModel):
    pdf_name: str
    start_page: int
    no_of_pages: Optional[int]

pdfRequest = PdfRequest

class SearchRequest(BaseModel):
    query: Optional[str] | None


searchRequest = SearchRequest

class UrlRequest(BaseModel):
    url: Optional[str] = None
    link: Optional[str] = None
    website: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_url_fallback(cls, data: Any) -> Any:
        if isinstance(data, dict):
            u = data.get("url") or data.get("link") or data.get("website") or ""
            data["url"] = u
        return data

# Alias for backwards compatibility
urlRequest = UrlRequest