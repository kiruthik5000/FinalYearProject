from typing import List, Dict, Any
from ingestion.websearch import WebSearch

class SearchController:

    def __init__(self):
        self.wb = WebSearch()
        # self.cont =
        pass

    def get_urls(self, query: str) -> List[str]:

        """
        Retrieves urls for given query
        :param query:
        :return:
        """

        try:
            urls = self.wb.get_urls(query)

            if len(urls) == 0:
                return list()

            return urls
        except Exception as e:
            return list()


    # def execute_websearch_query(self, urls: List[str], query: str) -> Dict[str, Any]: