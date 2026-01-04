import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set context to avoid undefined vars if any
os.environ['CONTEXT_PATH'] = ''

class TestAppStartup(unittest.TestCase):
    def test_imports(self):
        try:
            import flask
            print(f"Flask version: {flask.__version__}")
            from dashmachine import app
            
            # Use a testing config
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False
            app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:" 
            
            with app.test_client() as client:
                self.assertIn('main', app.blueprints)
                self.assertIn('user_system', app.blueprints)
                print("App structure loaded successfully")
                
        except ImportError as e:
            self.fail(f"Import failed (likely Flask/Werkzeug 3.x issue): {e}")
        except Exception as e:
            self.fail(f"App failed to initialize: {e}")

if __name__ == "__main__":
    unittest.main()
