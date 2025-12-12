"""
Strategy Evaluator Module
Evaluates and selects the best text chunking strategy
"""

import numpy as np
from typing import Dict, Tuple, List
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class StrategyMetrics:
    """Metrics for a chunking strategy"""
    strategy_name: str
    num_chunks: int
    avg_chunk_size: float
    chunk_size_std: float
    avg_similarity: float
    coverage_score: float
    total_score: float


class StrategyEvaluator:
    """Evaluates different chunking strategies"""

    @staticmethod
    def calculate_chunk_statistics(chunks: List[str]) -> Tuple[float, float]:
        """Calculate statistics about chunk sizes"""
        sizes = [len(chunk) for chunk in chunks]
        avg_size = np.mean(sizes)
        std_size = np.std(sizes)
        return avg_size, std_size

    @staticmethod
    def calculate_embedding_similarity(embeddings: List[List[float]]) -> float:
        """Calculate average cosine similarity between consecutive chunks"""
        if len(embeddings) < 2:
            return 0.0

        similarities = []
        for i in range(len(embeddings) - 1):
            emb1 = np.array(embeddings[i]).reshape(1, -1)
            emb2 = np.array(embeddings[i + 1]).reshape(1, -1)
            sim = cosine_similarity(emb1, emb2)[0][0]
            similarities.append(sim)

        return np.mean(similarities)

    @staticmethod
    def calculate_coverage_score(original_text: str, chunks: List[str]) -> float:
        """Calculate how well chunks cover the original text"""
        original_length = len(original_text)
        total_chunk_length = sum(len(chunk) for chunk in chunks)
        coverage = min(1.0, total_chunk_length / original_length)
        return coverage

    @classmethod
    def evaluate_strategy(
            cls,
            strategy_name: str,
            chunks: List[str],
            embeddings: List[List[float]],
            original_text: str
    ) -> StrategyMetrics:
        """Evaluate a single chunking strategy"""
        avg_size, std_size = cls.calculate_chunk_statistics(chunks)
        avg_similarity = cls.calculate_embedding_similarity(embeddings)
        coverage = cls.calculate_coverage_score(original_text, chunks)

        size_consistency = 1.0 / (1.0 + std_size / avg_size) if avg_size > 0 else 0
        similarity_score = 1.0 - abs(avg_similarity - 0.5) * 2

        total_score = (
                0.3 * coverage +
                0.3 * similarity_score +
                0.2 * size_consistency +
                0.2 * min(1.0, 50 / len(chunks))
        )

        return StrategyMetrics(
            strategy_name=strategy_name,
            num_chunks=len(chunks),
            avg_chunk_size=avg_size,
            chunk_size_std=std_size,
            avg_similarity=avg_similarity,
            coverage_score=coverage,
            total_score=total_score
        )

    @classmethod
    def select_best_strategy(
            cls,
            strategy_results: Dict,
            embedding_results: Dict,
            original_text: str
    ) -> Tuple[str, StrategyMetrics, Dict]:
        """Evaluate all strategies and select the best one"""
        print("\n" + "=" * 60)
        print("EVALUATING ALL STRATEGIES")
        print("=" * 60)

        all_metrics = {}

        for strategy_name in strategy_results.keys():
            chunks = strategy_results[strategy_name].chunks
            embeddings = embedding_results[strategy_name].embeddings

            metrics = cls.evaluate_strategy(
                strategy_name=strategy_name,
                chunks=chunks,
                embeddings=embeddings,
                original_text=original_text
            )

            all_metrics[strategy_name] = metrics

            print(f"\n{strategy_name.upper().replace('_', ' ')}:")
            print(f"  Chunks: {metrics.num_chunks}")
            print(f"  Avg Size: {metrics.avg_chunk_size:.1f} chars (±{metrics.chunk_size_std:.1f})")
            print(f"  Avg Similarity: {metrics.avg_similarity:.3f}")
            print(f"  Coverage: {metrics.coverage_score:.3f}")
            print(f"  → Total Score: {metrics.total_score:.3f}")

        best_strategy = max(all_metrics.items(), key=lambda x: x[1].total_score)
        best_name, best_metrics = best_strategy

        print("\n" + "=" * 60)
        print(f"🏆 BEST STRATEGY: {best_name.upper().replace('_', ' ')}")
        print(f"   Score: {best_metrics.total_score:.3f}")
        print("=" * 60)

        return best_name, best_metrics, all_metrics