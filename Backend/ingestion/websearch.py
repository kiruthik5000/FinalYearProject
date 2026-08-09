from typing import List
from ddgs import DDGS

class WebSearch:
    def __init__(self):
        pass

    def get_urls(self, query: str, max_results: int=5) -> List[str]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

                return [r["href"] for r in results]
        except Exception as e:
            print(f"Error occurs in websearch {e}")



if __name__ == '__main__':
    wb = WebSearch()

    print(wb.get_urls("what is mouse ?"))