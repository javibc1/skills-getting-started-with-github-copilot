import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Guardar el estado original
    original_activities = {k: v.copy() for k, v in activities.items()}
    for activity in original_activities.values():
        activity["participants"] = activity["participants"].copy()
    yield
    # Restaurar el estado original
    activities.clear()
    activities.update(original_activities)

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Asumiendo que hay actividades iniciales
    # Verificar que contiene las claves esperadas
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)

def test_signup_success(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()
    
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verificar que se agregó a la lista
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1

def test_signup_activity_not_found(client):
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up(client):
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]  # Usar un email ya registrado
    
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_unregister_success(client):
    activity_name = "Programming Class"
    email = activities[activity_name]["participants"][0]  # Usar un email registrado
    initial_participants = activities[activity_name]["participants"].copy()
    
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verificar que se removió de la lista
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1

def test_unregister_activity_not_found(client):
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"
    
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up(client):
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"  # Email no registrado
    
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]