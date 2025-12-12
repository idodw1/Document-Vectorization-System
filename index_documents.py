#!/usr/bin/env python3
"""
Document Indexing Script
Main script to process documents, create embeddings, and store in PostgreSQL

Usage:
    python index_documents.py <filepath>

Example:
    python index_documents.py documents/sample.pdf
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from database import Database

# Import our modules
from file_reader import FileReader
from text_splitter import TextSplitter
from embedding_generator import EmbeddingGenerator
from strategy_evaluator import StrategyEvaluator


# We'll add database import after creating database.py


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main(filepath: str):
    """
    Main processing pipeline

    Args:
        filepath: Path to the document file
    """
    print_header("DOCUMENT VECTORIZATION PIPELINE")
    print(f"File: {filepath}\n")

    try:
        # ===================================================================
        # STEP 1: READ FILE
        # ===================================================================
        print_header("STEP 1: READING FILE")

        text, filename = FileReader.read_file(filepath)

        if not text or len(text) < 100:
            print("✗ Error: File is too short or empty")
            return 1

        print(f"✓ Extracted {len(text):,} characters from {filename}")

        # ===================================================================
        # STEP 2: SPLIT TEXT WITH ALL STRATEGIES
        # ===================================================================
        print_header("STEP 2: SPLITTING TEXT")

        splitter = TextSplitter()
        strategy_results = splitter.split_all_strategies(text)

        # ===================================================================
        # STEP 3: GENERATE EMBEDDINGS
        # ===================================================================
        print_header("STEP 3: GENERATING EMBEDDINGS")

        generator = EmbeddingGenerator()
        embedding_results = generator.generate_for_all_strategies(strategy_results)

        # ===================================================================
        # STEP 4: EVALUATE STRATEGIES
        # ===================================================================
        print_header("STEP 4: EVALUATING STRATEGIES")

        best_strategy, best_metrics, all_metrics = StrategyEvaluator.select_best_strategy(
            strategy_results=strategy_results,
            embedding_results=embedding_results,
            original_text=text
        )

        # ===================================================================
        # STEP 5: SAVE TO DATABASE
        # ===================================================================
        print_header("STEP 5: SAVING TO POSTGRESQL")

        db = Database()
        # Table should already exist (run setup.py once to create it)

        # Get best strategy data
        best_chunks = strategy_results[best_strategy].chunks
        best_embeddings = embedding_results[best_strategy].embeddings

        # Save to database
        saved_count = db.save_chunks(
            filename=filename,
            chunks=best_chunks,
            embeddings=best_embeddings,
            strategy=best_strategy
        )

        print(f"✓ Saved {saved_count} chunks with strategy: {best_strategy}")

        # ===================================================================
        # SUMMARY
        # ===================================================================
        print_header("SUMMARY")
        print(f"File processed: {filename}")
        print(f"Original text: {len(text):,} characters")
        print(f"Best strategy: {best_strategy}")
        print(f"Score: {best_metrics.total_score:.3f}")
        print(f"Chunks created: {best_metrics.num_chunks}")
        print(f"Avg chunk size: {best_metrics.avg_chunk_size:.1f} chars")
        print(f"Coverage: {best_metrics.coverage_score:.1%}")
        print(f"Status: ✓ Processing complete (database save pending)")
        print("=" * 70)

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ File not found: {e}")
        return 1
    except ValueError as e:
        print(f"\n✗ Value error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Process documents and create vector embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python index_documents.py documents/sample.pdf
  python index_documents.py data/report.docx
        """
    )

    parser.add_argument(
        'filepath',
        help='Path to the document file (PDF or DOCX)'
    )

    args = parser.parse_args()

    # Verify file exists
    if not Path(args.filepath).exists():
        print(f"✗ Error: File not found: {args.filepath}")
        sys.exit(1)

    # Run main processing
    exit_code = main(args.filepath)
    sys.exit(exit_code)