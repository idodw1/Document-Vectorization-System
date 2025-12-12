#!/usr/bin/env python3
"""
Setup Script - Run Once
Creates the database table for document chunks
"""

from database import Database


def main():
    """Initialize database table"""
    print("=" * 60)
    print("DATABASE SETUP")
    print("=" * 60)

    try:
        db = Database()
        db.create_table()
        print("\n✓ Database setup complete!")
        print("\nYou can now run: python index_documents.py <file>")

    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())