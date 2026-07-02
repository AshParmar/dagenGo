"""
Chunker — Production-grade chunking with config-driven parameters.

Settings used:
  CHUNK_SIZE: 700 chars (≈175 tokens)
  CHUNK_OVERLAP: 120 chars (≈30 tokens)

Improvements:
  - Config-driven chunk size and overlap
  - Deduplication: skip chunks whose text has already been seen (hash-based)
  - Skip empty/whitespace-only chunks
  - Add source metadata for citation tracking
"""
import hashlib
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings

logger = logging.getLogger(__name__)


class Chunker:

    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
    ) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_documents(self, documents: list[dict]) -> list[dict]:
        chunks: list[dict] = []
        seen_hashes: set[str] = set()

        for document in documents:
            text = document.get("text", "")
            if not text or not text.strip():
                continue

            splits = self.splitter.split_text(text)

            for index, chunk_text in enumerate(splits):
                chunk_text = chunk_text.strip()
                if not chunk_text:
                    continue

                # Deduplicate chunks by content hash
                chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
                if chunk_hash in seen_hashes:
                    continue
                seen_hashes.add(chunk_hash)

                chunks.append(
                    {
                        "id": f'{document.get("url", "doc")}_{index}',
                        "text": chunk_text,
                        "title": document.get("title", ""),
                        "url": document.get("url", ""),
                        "source": document.get("domain") or document.get("url", ""),
                    }
                )

        logger.debug("Chunker: %d documents → %d unique chunks", len(documents), len(chunks))
        return chunks