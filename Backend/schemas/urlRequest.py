from typing import Optional, Any
from pydantic import BaseModel, model_validator

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
