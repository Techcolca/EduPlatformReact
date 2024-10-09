from flask.cli import FlaskGroup
from app import app, db
from models import User, Course
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

cli = FlaskGroup(app)

@cli.command("recreate_db")
def recreate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin_email = "admin@example.com"
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username="admin",
                email=admin_email,
                password_hash=generate_password_hash("admin_password"),
                is_admin=True
            )
            db.session.add(admin)
        
        # Create test user
        test_email = "test@example.com"
        if not User.query.filter_by(email=test_email).first():
            test_user = User(
                username="Test User",
                email=test_email,
                password_hash=generate_password_hash("password123"),
                areas_of_expertise="Testing",
                preferred_subjects="Unit Tests"
            )
            db.session.add(test_user)
        
        db.session.commit()
        print("Database recreated and seeded with initial data.")

@cli.command("check_schema")
def check_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"{table} table schema:")
            for column in columns:
                print(f"- {column['name']}: {column['type']}")

if __name__ == "__main__":
    cli()
