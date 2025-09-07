#!/usr/bin/env python3
"""
Database initialization script
Creates tables and loads initial data
"""

from models import init_db, SessionLocal, Project, Batch
from factors_loader import init_database_with_factors
import sys

def create_sample_project():
    """Create a sample project for testing"""
    db = SessionLocal()
    try:
        # Check if sample project exists
        existing = db.query(Project).filter(Project.name == "GreenStemGlobal").first()
        if existing:
            print("Sample project already exists")
            return
        
        # Create sample project
        project = Project(
            name="GreenStemGlobal",
            owner="GSG Operations",
            cbam_flag=True
        )
        db.add(project)
        db.commit()
        
        print(f"Created sample project: {project.name} (ID: {project.id})")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample project: {e}")
    finally:
        db.close()

def main():
    """Main initialization routine"""
    print("=" * 60)
    print("ESG Calculator Oracle - Database Initialization")
    print("=" * 60)
    
    try:
        # Initialize database with factors
        init_database_with_factors()
        
        # Create sample project
        create_sample_project()
        
        print("\n✅ Database initialization successful!")
        print("\nYou can now start the API server with:")
        print("  uvicorn app:app --reload")
        
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()