import logging
import trafilatura
from typing import List, Dict, Any
from file_extracter import Extractor

logger = logging.getLogger(__name__)


class WebSiteExtractor(Extractor):

    def extract(self, url: str) -> List[Dict[str, Any]]:
        """
        Extracts text from websites using trafilatura and chunks it.
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                logger.warning(f"Could not fetch content from URL: {url}")
                return []

            content = trafilatura.extract(downloaded)[:1000]
            if not content:
                logger.warning(f"Could not extract main text from URL: {url}")
                return []

            chunks = self.chunk_text(content)
            chunked_data = self.build_chunk_dicts(chunks, file_name=url, file_type="Website")
            logger.info(f"Created {len(chunked_data)} website chunks for {url}")
            return chunked_data

        except Exception as e:
            logger.error(f"Error extracting information from Website ({url}): {e}", exc_info=True)
            return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web = WebSiteExtractor()
    chunks = web.extract("https://www.geeksforgeeks.org/web-tech/what-is-web-socket-and-how-it-is-different-from-the-http/")
    if chunks:
        print(f"Total chunks: {len(chunks)}")
        print(chunks[0])