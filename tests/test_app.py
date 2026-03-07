import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Verify endpoint returns all activities with correct structure"""
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert set(activities.keys()) == expected_keys

    def test_get_activities_returns_activity_details(self, client):
        """Verify each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_details in activities.items():
            assert set(activity_details.keys()) == required_fields
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Verify student can sign up for an available activity"""
        # Arrange
        activity = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Verify signup fails for non-existent activity"""
        # Arrange
        activity = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student(self, client):
        """Verify student cannot sign up twice for the same activity"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"

    def test_signup_adds_to_participants_list(self, client):
        """Verify signup correctly updates participants list"""
        # Arrange
        activity = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        assert len(participants) == 2  # emma@mergington.edu + newstudent
        assert email in participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Verify student can unregister from an activity"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Verify unregister fails for non-existent activity"""
        # Arrange
        activity = "Non-existent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_participant_not_found(self, client):
        """Verify unregister fails if student is not in activity"""
        # Arrange
        activity = "Gym Class"
        email = "notasignedupstudent@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in activity"

    def test_unregister_removes_from_participants_list(self, client):
        """Verify unregister correctly updates participants list"""
        # Arrange
        activity = "Chess Club"
        email = "daniel@mergington.edu"
        initial_count = 2
        
        # Act
        client.post(f"/activities/{activity}/unregister?email={email}")
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        assert len(participants) == initial_count - 1
        assert email not in participants
        assert "michael@mergington.edu" in participants  # Other participant remains
