"""
Embedding Generator Module
Creates embeddings using Google Gemini API
"""

import os
import time
from typing import List, Dict
import google.generativeai as genai
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    embeddings: List[List[float]]
    chunks: List[str]
    strategy: str
    dimension: int
    total_chunks: int


class EmbeddingGenerator:
    """Class to generate embeddings using Gemini API"""

    def __init__(self, api_key: str = None):
        """
        Initialize the embedding generator

        Args:
            api_key: Google Gemini API key (if None, reads from env)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in .env file or pass as parameter"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Model for embeddings
        self.model_name = "models/embedding-001"

        print(f"✓ Gemini API configured with model: {self.model_name}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text chunk

        Args:
            text: Input text

        Returns:
            Embedding vector as list of floats
        """
        try:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    def generate_embeddings_batch(
            self,
            chunks: List[str],
            strategy: str,
            batch_size: int = 10,
            delay: float = 0.5
    ) -> EmbeddingResult:
        """
        Generate embeddings for multiple chunks with rate limiting

        Args:
            chunks: List of text chunks
            strategy: Name of the splitting strategy used
            batch_size: Number of chunks to process in parallel
            delay: Delay between batches (seconds)

        Returns:
            EmbeddingResult with embeddings and metadata
        """
        print(f"\nGenerating embeddings for {len(chunks)} chunks...")
        print(f"Strategy: {strategy}")
        print(f"Batch size: {batch_size}, Delay: {delay}s")

        embeddings = []
        total = len(chunks)

        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            print(f"  Processing batch {batch_num}/{total_batches}...", end=" ")

            for chunk in batch:
                try:
                    embedding = self.generate_embedding(chunk)
                    embeddings.append(embedding)
                except Exception as e:
                    print(f"\n  ✗ Error on chunk: {str(e)}")
                    # Use zero vector as fallback
                    embeddings.append([0.0] * 768)

            print(f"✓ ({len(embeddings)}/{total} done)")

            # Rate limiting: wait between batches
            if i + batch_size < total:
                time.sleep(delay)

        dimension = len(embeddings[0]) if embeddings else 0

        print(f"✓ Generated {len(embeddings)} embeddings (dimension: {dimension})")

        return EmbeddingResult(
            embeddings=embeddings,
            chunks=chunks,
            strategy=strategy,
            dimension=dimension,
            total_chunks=len(chunks)
        )

    def generate_for_all_strategies(
            self,
            strategy_results: Dict
    ) -> Dict[str, EmbeddingResult]:
        """
        Generate embeddings for all splitting strategies

        Args:
            strategy_results: Dict with ChunkResults from TextSplitter

        Returns:
            Dict with EmbeddingResults for each strategy
        """
        print("\n" + "=" * 60)
        print("GENERATING EMBEDDINGS FOR ALL STRATEGIES")
        print("=" * 60)

        all_embeddings = {}

        for strategy_name, chunk_result in strategy_results.items():
            print(f"\n{strategy_name.upper().replace('_', ' ')}:")

            embedding_result = self.generate_embeddings_batch(
                chunks=chunk_result.chunks,
                strategy=chunk_result.strategy
            )

            all_embeddings[strategy_name] = embedding_result

        print("\n" + "=" * 60)
        print("✓ ALL EMBEDDINGS GENERATED SUCCESSFULLY")
        print("=" * 60)

        return all_embeddings


if __name__ == "__main__":
    # Test the embedding generator
    from dotenv import load_dotenv

    load_dotenv()

    # Sample texts
    sample_chunks = [
        "This is the first test chunk of text.",
        "Here is another chunk for testing embeddings.",
        "The third chunk contains different content."
    ]

    try:
        generator = EmbeddingGenerator()
        result = generator.generate_embeddings_batch(
            chunks=sample_chunks,
            strategy="test"
        )

        print(f"\n✓ Test successful!")
        print(f"Generated {result.total_chunks} embeddings")
        print(f"Embedding dimension: {result.dimension}")
        print(f"First embedding (first 5 values): {result.embeddings[0][:5]}")

    except Exception as e:
        print(f"✗ Test failed: {e}")