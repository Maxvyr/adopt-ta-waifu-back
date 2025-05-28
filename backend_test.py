import requests
import json
import time
import uuid
from typing import Dict, List, Any, Optional

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://1d5ce834-e7ae-4e90-8ec1-af620a67bce0.preview.emergentagent.com/api"

class IdeaLoggerAPITest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.test_ideas = []
        self.test_results = {
            "Ideas CRUD API endpoints": {"success": True, "details": []},
            "Search and filtering API": {"success": True, "details": []},
            "Categories and tags management API": {"success": True, "details": []}
        }
    
    def run_all_tests(self):
        """Run all test cases"""
        print("Starting API tests for Idea Logger backend...")
        
        # Test basic API connectivity
        self.test_api_connectivity()
        
        # Test CRUD operations
        self.test_create_idea()
        self.test_get_all_ideas()
        self.test_get_idea_by_id()
        self.test_update_idea()
        
        # Test search and filtering
        self.test_search_ideas()
        self.test_filter_by_status()
        self.test_filter_by_category()
        self.test_filter_by_tags()
        self.test_combined_filters()
        
        # Test archive/unarchive
        self.test_archive_idea()
        self.test_unarchive_idea()
        
        # Test categories and tags
        self.test_get_categories()
        self.test_get_tags()
        
        # Test deletion (do this last)
        self.test_delete_idea()
        
        # Clean up any remaining test ideas
        self.cleanup_test_ideas()
        
        # Print summary
        self.print_summary()
        
        return self.test_results
    
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.base_url}/")
            assert response.status_code == 200
            assert "message" in response.json()
            print("✅ API connectivity test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("API connectivity test passed")
        except Exception as e:
            print(f"❌ API connectivity test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"API connectivity test failed: {str(e)}")
    
    def test_create_idea(self):
        """Test creating a new idea"""
        try:
            # Create multiple ideas with different categories and tags
            ideas_to_create = [
                {
                    "title": f"Test Idea 1 {uuid.uuid4()}",
                    "content": "This is a test idea with programming tags",
                    "tags": ["python", "api", "testing"],
                    "category": "Programming"
                },
                {
                    "title": f"Test Idea 2 {uuid.uuid4()}",
                    "content": "This is a test idea with design tags",
                    "tags": ["ui", "ux", "design"],
                    "category": "Design"
                },
                {
                    "title": f"Test Idea 3 {uuid.uuid4()}",
                    "content": "This is a test idea with business tags",
                    "tags": ["startup", "business", "marketing"],
                    "category": "Business"
                }
            ]
            
            for idea_data in ideas_to_create:
                response = requests.post(f"{self.base_url}/ideas", json=idea_data)
                assert response.status_code == 200
                created_idea = response.json()
                
                # Verify all fields were saved correctly
                for key, value in idea_data.items():
                    assert created_idea[key] == value
                
                # Verify additional fields
                assert "id" in created_idea
                assert "created_at" in created_idea
                assert "updated_at" in created_idea
                assert created_idea["status"] == "active"
                
                # Save the created idea for later tests
                self.test_ideas.append(created_idea)
            
            print(f"✅ Create idea test passed - Created {len(ideas_to_create)} ideas")
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Create idea test passed - Created {len(ideas_to_create)} ideas")
        except Exception as e:
            print(f"❌ Create idea test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Create idea test failed: {str(e)}")
    
    def test_get_all_ideas(self):
        """Test getting all ideas"""
        try:
            response = requests.get(f"{self.base_url}/ideas")
            assert response.status_code == 200
            ideas = response.json()
            
            # Verify we get a list of ideas
            assert isinstance(ideas, list)
            
            # Verify our test ideas are in the list
            test_idea_ids = [idea["id"] for idea in self.test_ideas]
            found_ideas = [idea for idea in ideas if idea["id"] in test_idea_ids]
            assert len(found_ideas) == len(self.test_ideas)
            
            print(f"✅ Get all ideas test passed - Found {len(ideas)} ideas")
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Get all ideas test passed - Found {len(ideas)} ideas")
        except Exception as e:
            print(f"❌ Get all ideas test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Get all ideas test failed: {str(e)}")
    
    def test_get_idea_by_id(self):
        """Test getting a specific idea by ID"""
        if not self.test_ideas:
            print("⚠️ Skipping get idea by ID test - No test ideas available")
            return
        
        try:
            idea_id = self.test_ideas[0]["id"]
            response = requests.get(f"{self.base_url}/ideas/{idea_id}")
            assert response.status_code == 200
            idea = response.json()
            
            # Verify it's the correct idea
            assert idea["id"] == idea_id
            assert idea["title"] == self.test_ideas[0]["title"]
            assert idea["content"] == self.test_ideas[0]["content"]
            
            # Test with non-existent ID
            fake_id = str(uuid.uuid4())
            response = requests.get(f"{self.base_url}/ideas/{fake_id}")
            assert response.status_code == 404
            
            print("✅ Get idea by ID test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("Get idea by ID test passed")
        except Exception as e:
            print(f"❌ Get idea by ID test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Get idea by ID test failed: {str(e)}")
    
    def test_update_idea(self):
        """Test updating an idea"""
        if not self.test_ideas:
            print("⚠️ Skipping update idea test - No test ideas available")
            return
        
        try:
            idea_id = self.test_ideas[0]["id"]
            update_data = {
                "title": f"Updated Title {uuid.uuid4()}",
                "content": "This content has been updated",
                "tags": ["updated", "testing", "api"]
            }
            
            response = requests.put(f"{self.base_url}/ideas/{idea_id}", json=update_data)
            assert response.status_code == 200
            updated_idea = response.json()
            
            # Verify fields were updated
            assert updated_idea["title"] == update_data["title"]
            assert updated_idea["content"] == update_data["content"]
            assert updated_idea["tags"] == update_data["tags"]
            
            # Verify other fields remain unchanged
            assert updated_idea["category"] == self.test_ideas[0]["category"]
            assert updated_idea["status"] == self.test_ideas[0]["status"]
            
            # Update the stored test idea
            self.test_ideas[0] = updated_idea
            
            # Test with non-existent ID
            fake_id = str(uuid.uuid4())
            response = requests.put(f"{self.base_url}/ideas/{fake_id}", json=update_data)
            assert response.status_code == 404
            
            print("✅ Update idea test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("Update idea test passed")
        except Exception as e:
            print(f"❌ Update idea test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Update idea test failed: {str(e)}")
    
    def test_delete_idea(self):
        """Test deleting an idea"""
        if not self.test_ideas:
            print("⚠️ Skipping delete idea test - No test ideas available")
            return
        
        try:
            # Use the last test idea for deletion
            idea_id = self.test_ideas[-1]["id"]
            response = requests.delete(f"{self.base_url}/ideas/{idea_id}")
            assert response.status_code == 200
            
            # Verify the idea is deleted
            response = requests.get(f"{self.base_url}/ideas/{idea_id}")
            assert response.status_code == 404
            
            # Remove the deleted idea from our list
            self.test_ideas.pop()
            
            # Test with non-existent ID
            fake_id = str(uuid.uuid4())
            response = requests.delete(f"{self.base_url}/ideas/{fake_id}")
            assert response.status_code == 404
            
            print("✅ Delete idea test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("Delete idea test passed")
        except Exception as e:
            print(f"❌ Delete idea test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Delete idea test failed: {str(e)}")
    
    def test_search_ideas(self):
        """Test searching ideas by text"""
        if not self.test_ideas:
            print("⚠️ Skipping search ideas test - No test ideas available")
            return
        
        try:
            # Search by title
            title_fragment = self.test_ideas[0]["title"].split()[1]  # Use a word from the title
            response = requests.get(f"{self.base_url}/ideas?search={title_fragment}")
            assert response.status_code == 200
            search_results = response.json()
            
            # Verify search results
            assert len(search_results) > 0
            found = False
            for idea in search_results:
                if idea["id"] == self.test_ideas[0]["id"]:
                    found = True
                    break
            assert found, "Test idea not found in search results"
            
            # Search by content
            content_fragment = "test idea"  # Common phrase in our test ideas
            response = requests.get(f"{self.base_url}/ideas?search={content_fragment}")
            assert response.status_code == 200
            search_results = response.json()
            
            # Verify search results
            assert len(search_results) > 0
            
            # Test empty search
            response = requests.get(f"{self.base_url}/ideas?search=")
            assert response.status_code == 200
            
            # Test search with no results
            random_search = f"nonexistent{uuid.uuid4()}"
            response = requests.get(f"{self.base_url}/ideas?search={random_search}")
            assert response.status_code == 200
            assert len(response.json()) == 0
            
            print("✅ Search ideas test passed")
            self.test_results["Search and filtering API"]["details"].append("Search ideas test passed")
        except Exception as e:
            print(f"❌ Search ideas test failed: {str(e)}")
            self.test_results["Search and filtering API"]["success"] = False
            self.test_results["Search and filtering API"]["details"].append(f"Search ideas test failed: {str(e)}")
    
    def test_filter_by_status(self):
        """Test filtering ideas by status"""
        if not self.test_ideas:
            print("⚠️ Skipping filter by status test - No test ideas available")
            return
        
        try:
            # Filter by active status
            response = requests.get(f"{self.base_url}/ideas?status=active")
            assert response.status_code == 200
            active_ideas = response.json()
            
            # Verify all returned ideas have active status
            for idea in active_ideas:
                assert idea["status"] == "active"
            
            # Filter by archived status
            response = requests.get(f"{self.base_url}/ideas?status=archived")
            assert response.status_code == 200
            archived_ideas = response.json()
            
            # Verify all returned ideas have archived status
            for idea in archived_ideas:
                assert idea["status"] == "archived"
            
            print("✅ Filter by status test passed")
            self.test_results["Search and filtering API"]["details"].append("Filter by status test passed")
        except Exception as e:
            print(f"❌ Filter by status test failed: {str(e)}")
            self.test_results["Search and filtering API"]["success"] = False
            self.test_results["Search and filtering API"]["details"].append(f"Filter by status test failed: {str(e)}")
    
    def test_filter_by_category(self):
        """Test filtering ideas by category"""
        if not self.test_ideas:
            print("⚠️ Skipping filter by category test - No test ideas available")
            return
        
        try:
            # Get a category from our test ideas
            category = self.test_ideas[0]["category"]
            
            # Filter by that category
            response = requests.get(f"{self.base_url}/ideas?category={category}")
            assert response.status_code == 200
            category_ideas = response.json()
            
            # Verify all returned ideas have the specified category
            for idea in category_ideas:
                assert idea["category"] == category
            
            # Verify our test idea is in the results
            found = False
            for idea in category_ideas:
                if idea["id"] == self.test_ideas[0]["id"]:
                    found = True
                    break
            assert found, "Test idea not found in category filter results"
            
            print("✅ Filter by category test passed")
            self.test_results["Search and filtering API"]["details"].append("Filter by category test passed")
        except Exception as e:
            print(f"❌ Filter by category test failed: {str(e)}")
            self.test_results["Search and filtering API"]["success"] = False
            self.test_results["Search and filtering API"]["details"].append(f"Filter by category test failed: {str(e)}")
    
    def test_filter_by_tags(self):
        """Test filtering ideas by tags"""
        if not self.test_ideas:
            print("⚠️ Skipping filter by tags test - No test ideas available")
            return
        
        try:
            # Get a tag from our test ideas
            tag = self.test_ideas[0]["tags"][0]
            
            # Filter by that tag
            response = requests.get(f"{self.base_url}/ideas?tags={tag}")
            assert response.status_code == 200
            tag_ideas = response.json()
            
            # Verify all returned ideas have the specified tag
            for idea in tag_ideas:
                assert tag in idea["tags"]
            
            # Test multiple tags
            if len(self.test_ideas) >= 2 and self.test_ideas[1]["tags"]:
                tag2 = self.test_ideas[1]["tags"][0]
                response = requests.get(f"{self.base_url}/ideas?tags={tag},{tag2}")
                assert response.status_code == 200
                multi_tag_ideas = response.json()
                
                # Verify all returned ideas have at least one of the specified tags
                for idea in multi_tag_ideas:
                    assert any(t in idea["tags"] for t in [tag, tag2])
            
            print("✅ Filter by tags test passed")
            self.test_results["Search and filtering API"]["details"].append("Filter by tags test passed")
        except Exception as e:
            print(f"❌ Filter by tags test failed: {str(e)}")
            self.test_results["Search and filtering API"]["success"] = False
            self.test_results["Search and filtering API"]["details"].append(f"Filter by tags test failed: {str(e)}")
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        if not self.test_ideas:
            print("⚠️ Skipping combined filters test - No test ideas available")
            return
        
        try:
            # Get values from our test ideas
            category = self.test_ideas[0]["category"]
            tag = self.test_ideas[0]["tags"][0]
            status = "active"
            
            # Combine filters
            response = requests.get(f"{self.base_url}/ideas?category={category}&tags={tag}&status={status}")
            assert response.status_code == 200
            filtered_ideas = response.json()
            
            # Verify all returned ideas match all criteria
            for idea in filtered_ideas:
                assert idea["category"] == category
                assert tag in idea["tags"]
                assert idea["status"] == status
            
            print("✅ Combined filters test passed")
            self.test_results["Search and filtering API"]["details"].append("Combined filters test passed")
        except Exception as e:
            print(f"❌ Combined filters test failed: {str(e)}")
            self.test_results["Search and filtering API"]["success"] = False
            self.test_results["Search and filtering API"]["details"].append(f"Combined filters test failed: {str(e)}")
    
    def test_archive_idea(self):
        """Test archiving an idea"""
        if not self.test_ideas:
            print("⚠️ Skipping archive idea test - No test ideas available")
            return
        
        try:
            # Use the first test idea for archiving
            idea_id = self.test_ideas[0]["id"]
            response = requests.patch(f"{self.base_url}/ideas/{idea_id}/archive")
            assert response.status_code == 200
            
            # Verify the idea is archived
            response = requests.get(f"{self.base_url}/ideas/{idea_id}")
            assert response.status_code == 200
            idea = response.json()
            assert idea["status"] == "archived"
            
            # Update our test idea
            self.test_ideas[0]["status"] = "archived"
            
            # Test with non-existent ID
            fake_id = str(uuid.uuid4())
            response = requests.patch(f"{self.base_url}/ideas/{fake_id}/archive")
            assert response.status_code == 404
            
            print("✅ Archive idea test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("Archive idea test passed")
        except Exception as e:
            print(f"❌ Archive idea test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Archive idea test failed: {str(e)}")
    
    def test_unarchive_idea(self):
        """Test unarchiving an idea"""
        if not self.test_ideas:
            print("⚠️ Skipping unarchive idea test - No test ideas available")
            return
        
        try:
            # Use the first test idea for unarchiving (should be archived from previous test)
            idea_id = self.test_ideas[0]["id"]
            response = requests.patch(f"{self.base_url}/ideas/{idea_id}/unarchive")
            assert response.status_code == 200
            
            # Verify the idea is unarchived
            response = requests.get(f"{self.base_url}/ideas/{idea_id}")
            assert response.status_code == 200
            idea = response.json()
            assert idea["status"] == "active"
            
            # Update our test idea
            self.test_ideas[0]["status"] = "active"
            
            # Test with non-existent ID
            fake_id = str(uuid.uuid4())
            response = requests.patch(f"{self.base_url}/ideas/{fake_id}/unarchive")
            assert response.status_code == 404
            
            print("✅ Unarchive idea test passed")
            self.test_results["Ideas CRUD API endpoints"]["details"].append("Unarchive idea test passed")
        except Exception as e:
            print(f"❌ Unarchive idea test failed: {str(e)}")
            self.test_results["Ideas CRUD API endpoints"]["success"] = False
            self.test_results["Ideas CRUD API endpoints"]["details"].append(f"Unarchive idea test failed: {str(e)}")
    
    def test_get_categories(self):
        """Test getting all unique categories"""
        try:
            response = requests.get(f"{self.base_url}/categories")
            assert response.status_code == 200
            data = response.json()
            
            # Verify we get a list of categories
            assert "categories" in data
            assert isinstance(data["categories"], list)
            
            # If we have test ideas, verify their categories are in the list
            if self.test_ideas:
                test_categories = set(idea["category"] for idea in self.test_ideas)
                for category in test_categories:
                    assert category in data["categories"]
            
            print("✅ Get categories test passed")
            self.test_results["Categories and tags management API"]["details"].append("Get categories test passed")
        except Exception as e:
            print(f"❌ Get categories test failed: {str(e)}")
            self.test_results["Categories and tags management API"]["success"] = False
            self.test_results["Categories and tags management API"]["details"].append(f"Get categories test failed: {str(e)}")
    
    def test_get_tags(self):
        """Test getting all unique tags"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            assert response.status_code == 200
            data = response.json()
            
            # Verify we get a list of tags
            assert "tags" in data
            assert isinstance(data["tags"], list)
            
            # If we have test ideas, verify their tags are in the list
            if self.test_ideas:
                test_tags = set()
                for idea in self.test_ideas:
                    test_tags.update(idea["tags"])
                
                for tag in test_tags:
                    assert tag in data["tags"]
            
            print("✅ Get tags test passed")
            self.test_results["Categories and tags management API"]["details"].append("Get tags test passed")
        except Exception as e:
            print(f"❌ Get tags test failed: {str(e)}")
            self.test_results["Categories and tags management API"]["success"] = False
            self.test_results["Categories and tags management API"]["details"].append(f"Get tags test failed: {str(e)}")
    
    def cleanup_test_ideas(self):
        """Clean up any remaining test ideas"""
        print(f"Cleaning up {len(self.test_ideas)} test ideas...")
        for idea in self.test_ideas[:]:
            try:
                requests.delete(f"{self.base_url}/ideas/{idea['id']}")
                self.test_ideas.remove(idea)
            except Exception as e:
                print(f"Warning: Failed to delete test idea {idea['id']}: {str(e)}")
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n=== TEST SUMMARY ===")
        
        all_passed = True
        for task, result in self.test_results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            if not result["success"]:
                all_passed = False
            
            print(f"{task}: {status}")
            for detail in result["details"]:
                print(f"  - {detail}")
        
        if all_passed:
            print("\n🎉 All tests passed successfully!")
        else:
            print("\n⚠️ Some tests failed. See details above.")

if __name__ == "__main__":
    tester = IdeaLoggerAPITest(BACKEND_URL)
    results = tester.run_all_tests()