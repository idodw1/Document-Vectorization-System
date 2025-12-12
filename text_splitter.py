"""
Text Splitter Module
Implements three different text chunking strategies
"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class ChunkResult:
    """Result of text chunking"""
    chunks: List[str]
    strategy: str
    num_chunks: int
    avg_chunk_size: float


class TextSplitter:
    """Class to handle different text splitting strategies"""

    @staticmethod
    def fixed_size_with_overlap(
            text: str,
            chunk_size: int = 500,
            overlap: int = 50
    ) -> ChunkResult:
        """
        Split text into fixed-size chunks with overlap

        Args:
            text: Input text to split
            chunk_size: Size of each chunk in characters
            overlap: Number of overlapping characters between chunks

        Returns:
            ChunkResult with chunks and metadata
        """
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size")

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

            # Move start position forward by (chunk_size - overlap)
            start += (chunk_size - overlap)

        avg_size = sum(len(c) for c in chunks) / len(chunks) if chunks else 0

        return ChunkResult(
            chunks=chunks,
            strategy="fixed_size_with_overlap",
            num_chunks=len(chunks),
            avg_chunk_size=avg_size
        )

    @staticmethod
    def sentence_based_splitting(
            text: str,
            sentences_per_chunk: int = 5
    ) -> ChunkResult:
        """
        Split text based on sentences

        Args:
            text: Input text to split
            sentences_per_chunk: Number of sentences per chunk

        Returns:
            ChunkResult with chunks and metadata
        """
        # Split by sentence endings (., !, ?)
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)

        # Remove empty sentences and strip whitespace
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk_sentences = sentences[i:i + sentences_per_chunk]
            chunk = " ".join(chunk_sentences)
            if chunk:
                chunks.append(chunk)

        avg_size = sum(len(c) for c in chunks) / len(chunks) if chunks else 0

        return ChunkResult(
            chunks=chunks,
            strategy="sentence_based",
            num_chunks=len(chunks),
            avg_chunk_size=avg_size
        )

    @staticmethod
    def paragraph_based_splitting(
            text: str,
            min_paragraph_length: int = 100
    ) -> ChunkResult:
        """
        Split text based on paragraphs

        Args:
            text: Input text to split
            min_paragraph_length: Minimum length for a paragraph

        Returns:
            ChunkResult with chunks and metadata
        """
        # Split by double newlines or multiple whitespace
        paragraphs = re.split(r'\n\s*\n', text)

        chunks = []
        for para in paragraphs:
            para = para.strip()

            # Only include paragraphs that meet minimum length
            if len(para) >= min_paragraph_length:
                chunks.append(para)
            elif chunks:
                # If paragraph is too short, append to previous chunk
                chunks[-1] += " " + para

        # If no chunks were created, create one chunk
        if not chunks and text.strip():
            chunks = [text.strip()]

        avg_size = sum(len(c) for c in chunks) / len(chunks) if chunks else 0

        return ChunkResult(
            chunks=chunks,
            strategy="paragraph_based",
            num_chunks=len(chunks),
            avg_chunk_size=avg_size
        )

    @classmethod
    def split_all_strategies(cls, text: str) -> dict:
        """
        Split text using all three strategies

        Args:
            text: Input text to split

        Returns:
            Dictionary with results from all strategies
        """
        print("\n" + "=" * 60)
        print("SPLITTING TEXT WITH ALL STRATEGIES")
        print("=" * 60)

        results = {}

        # Strategy 1: Fixed size with overlap
        print("\n1. Fixed Size with Overlap (500 chars, 50 overlap)...")
        fixed_result = cls.fixed_size_with_overlap(text)
        results['fixed_size'] = fixed_result
        print(f"   ✓ Created {fixed_result.num_chunks} chunks")
        print(f"   ✓ Average chunk size: {fixed_result.avg_chunk_size:.1f} characters")

        # Strategy 2: Sentence-based
        print("\n2. Sentence-Based Splitting (5 sentences per chunk)...")
        sentence_result = cls.sentence_based_splitting(text)
        results['sentence_based'] = sentence_result
        print(f"   ✓ Created {sentence_result.num_chunks} chunks")
        print(f"   ✓ Average chunk size: {sentence_result.avg_chunk_size:.1f} characters")

        # Strategy 3: Paragraph-based
        print("\n3. Paragraph-Based Splitting (min 100 chars)...")
        paragraph_result = cls.paragraph_based_splitting(text)
        results['paragraph_based'] = paragraph_result
        print(f"   ✓ Created {paragraph_result.num_chunks} chunks")
        print(f"   ✓ Average chunk size: {paragraph_result.avg_chunk_size:.1f} characters")

        print("\n" + "=" * 60)

        return results


if __name__ == "__main__":
    # Test the text splitter
    sample_text = """
    This is the first sentence. This is the second sentence. This is the third sentence.
    This is the fourth sentence. This is the fifth sentence.

    This is a new paragraph with more content. It has multiple sentences.
    Each sentence adds to the overall meaning.

    Here is another paragraph. It's separate from the previous ones.
    The content continues to grow.
    """ * 10

    splitter = TextSplitter()
    results = splitter.split_all_strategies(sample_text)

    print("\nSample chunks from each strategy:")
    for strategy_name, result in results.items():
        print(f"\n{strategy_name}:")
        print(f"First chunk: {result.chunks[0][:100]}...")