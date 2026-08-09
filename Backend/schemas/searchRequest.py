from typing import Optional, List

from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: Optional[str] | None


searchRequest = SearchRequest