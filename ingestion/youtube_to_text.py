import logging
from typing import List, Dict, Any
from file_extracter import Extractor
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


class YouTubeExtractor(Extractor):

    def __init__(self):
        self.api = YouTubeTranscriptApi()

    def extract(self, url: str) -> List[Dict[str, Any]]:
        """
        Extracts text transcript from YouTube video URL and chunks it.
        """
        try:
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                video_id = url.split("/")[-1].split("?")[0]

            transcript = self.api.fetch(video_id) if hasattr(self.api, 'fetch') else YouTubeTranscriptApi.get_transcript(video_id)
            content = " ".join([
                snippet.get('text', '') if isinstance(snippet, dict) else getattr(snippet, 'text', str(snippet))
                for snippet in transcript
            ])

            if not content.strip():
                logger.warning(f"No transcript content retrieved for YouTube video ID: {video_id}")
                return []

            chunks = self.chunk_text(content)
            chunked_data = self.build_chunk_dicts(chunks, file_name=url, file_type="YouTube")
            logger.info(f"Created {len(chunked_data)} YouTube transcript chunks for {url}")
            return chunked_data

        except Exception as e:
            logger.error(f"Error extracting transcript from YouTube URL ({url}): {e}", exc_info=True)
            return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    yt = YouTubeExtractor()
    chunks = yt.extract("https://youtu.be/i8NETqtGHms")
    if chunks:
        print(f"Total chunks: {len(chunks)}")
        print(chunks[0])