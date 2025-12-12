"""
Database Module
Handles PostgreSQL operations for storing document chunks and embeddings
"""

import os
import psycopg
from psycopg import sql
from typing import List, Dict
from dotenv import load_dotenv


class Database:
    """PostgreSQL database handler for document embeddings"""

    def __init__(self):
        """Initialize database connection"""
        load_dotenv()
        self.connection_string = os.getenv('POSTGRES_URL')

        if not self.connection_string:
            raise ValueError("POSTGRES_URL not found in environment variables")

        # Test connection
        try:
            with psycopg.connect(self.connection_string) as conn:
                print("✓ Database connection successful")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def create_table(self):
        """Create the document_chunks table if it doesn't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            embedding_vector REAL[] NOT NULL,
            split_strategy VARCHAR(50) NOT NULL,
            chunk_size INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_filename ON document_chunks(filename);
        CREATE INDEX IF NOT EXISTS idx_strategy ON document_chunks(split_strategy);
        """

        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    conn.commit()
            print("✓ Table 'document_chunks' ready")
        except Exception as e:
            raise RuntimeError(f"Failed to create table: {e}")

    def save_chunks(
            self,
            filename: str,
            chunks: List[str],
            embeddings: List[List[float]],
            strategy: str
    ) -> int:
        """
        Save document chunks and their embeddings to database

        Args:
            filename: Name of the source document
            chunks: List of text chunks
            embeddings: List of embedding vectors
            strategy: Name of the splitting strategy used

        Returns:
            Number of chunks saved
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks count ({len(chunks)}) doesn't match embeddings count ({len(embeddings)})"
            )

        insert_query = """
        INSERT INTO document_chunks 
            (filename, chunk_text, chunk_index, embedding_vector, split_strategy, chunk_size)
        VALUES 
            (%s, %s, %s, %s, %s, %s)
        """

        saved_count = 0

        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                        cursor.execute(
                            insert_query,
                            (
                                filename,
                                chunk,
                                idx,
                                embedding,  # psycopg3 handles list → array conversion
                                strategy,
                                len(chunk)
                            )
                        )
                        saved_count += 1

                    conn.commit()

            print(f"✓ Saved {saved_count} chunks to database")
            return saved_count

        except Exception as e:
            raise RuntimeError(f"Failed to save chunks: {e}")

    def get_chunks_by_filename(self, filename: str) -> List[Dict]:
        """
        Retrieve all chunks for a specific filename

        Args:
            filename: Name of the document

        Returns:
            List of dictionaries containing chunk data
        """
        query = """
        SELECT 
            id, filename, chunk_text, chunk_index, 
            split_strategy, chunk_size, created_at
        FROM document_chunks
        WHERE filename = %s
        ORDER BY chunk_index
        """

        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (filename,))
                    rows = cursor.fetchall()

                    results = []
                    for row in rows:
                        results.append({
                            'id': row[0],
                            'filename': row[1],
                            'chunk_text': row[2],
                            'chunk_index': row[3],
                            'split_strategy': row[4],
                            'chunk_size': row[5],
                            'created_at': row[6]
                        })

                    return results

        except Exception as e:
            raise RuntimeError(f"Failed to retrieve chunks: {e}")

    def delete_chunks_by_filename(self, filename: str) -> int:
        """
        Delete all chunks for a specific filename

        Args:
            filename: Name of the document

        Returns:
            Number of chunks deleted
        """
        query = "DELETE FROM document_chunks WHERE filename = %s"

        try:
            with psycopg.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (filename,))
                    deleted_count = cursor.rowcount
                    conn.commit()

            print(f"✓ Deleted {deleted_count} chunks")
            return deleted_count

        except Exception as e:
            raise RuntimeError(f"Failed to delete chunks: {e}")


if __name__ == "__main__":
    # Test the database module
    print("Testing Database Module...")

    try:
        db = Database()
        db.create_table()
        print("✓ Database module working correctly!")

    except Exception as e:
        print(f"✗ Error: {e}")