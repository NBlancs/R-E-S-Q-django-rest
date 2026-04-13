from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Camera, Incident, UserProfile

User = get_user_model()


class AuthenticationTests(TestCase):
	"""Test authentication endpoints: register, login, profile"""

	def setUp(self):
		self.client = APIClient()
		self.register_url = "/api/auth/register/"
		self.login_url = "/api/auth/login/"
		self.profile_url = "/api/auth/profile/"

	def test_register_success(self):
		"""Test successful user registration"""
		data = {
			"email": "testuser@gmail.com",
			"password": "testpass123",
			"username": "testuser",
			"role": "bfp",
		}
		response = self.client.post(self.register_url, data)
		
		self.assertEqual(response.status_code, 201)
		self.assertIn("token", response.data)
		self.assertIn("user", response.data)
		self.assertEqual(response.data["user"]["email"], "testuser@gmail.com")
		self.assertTrue(User.objects.filter(email="testuser@gmail.com").exists())

	def test_register_auto_generate_username(self):
		"""Test that username is auto-generated from email if not provided"""
		data = {
			"email": "newuser@gmail.com",
			"password": "testpass123",
		}
		response = self.client.post(self.register_url, data)
		
		self.assertEqual(response.status_code, 201)
		user = User.objects.get(email="newuser@gmail.com")
		self.assertEqual(user.username, "newuser")

	def test_register_duplicate_email(self):
		"""Test that duplicate email registration fails"""
		User.objects.create_user(
			username="existing",
			email="existing@gmail.com",
			password="pass123",
		)
		
		data = {
			"email": "existing@gmail.com",
			"password": "testpass123",
		}
		response = self.client.post(self.register_url, data)
		
		self.assertEqual(response.status_code, 400)
		self.assertIn("Email is already registered", str(response.data))

	def test_register_invalid_email(self):
		"""Test that invalid email is rejected"""
		data = {
			"email": "not-an-email",
			"password": "testpass123",
		}
		response = self.client.post(self.register_url, data)
		
		self.assertEqual(response.status_code, 400)

	def test_register_short_password(self):
		"""Test that password below minimum length is rejected"""
		data = {
			"email": "user@gmail.com",
			"password": "short",
		}
		response = self.client.post(self.register_url, data)
		
		self.assertEqual(response.status_code, 400)

	def test_login_success(self):
		"""Test successful login"""
		user = User.objects.create_user(
			username="testuser",
			email="testuser@gmail.com",
			password="testpass123",
		)
		UserProfile.objects.create(user=user, role=UserProfile.ROLE_BFP)
		
		data = {
			"email": "testuser@gmail.com",
			"password": "testpass123",
		}
		response = self.client.post(self.login_url, data)
		
		self.assertEqual(response.status_code, 200)
		self.assertIn("token", response.data)
		self.assertEqual(response.data["user"]["email"], "testuser@gmail.com")

	def test_login_invalid_credentials(self):
		"""Test login with wrong password"""
		User.objects.create_user(
			username="testuser",
			email="testuser@gmail.com",
			password="testpass123",
		)
		
		data = {
			"email": "testuser@gmail.com",
			"password": "wrongpassword",
		}
		response = self.client.post(self.login_url, data)
		
		self.assertEqual(response.status_code, 401)

	def test_login_nonexistent_user(self):
		"""Test login with non-existent email"""
		data = {
			"email": "nonexistent@gmail.com",
			"password": "anypassword",
		}
		response = self.client.post(self.login_url, data)
		
		self.assertEqual(response.status_code, 401)

	def test_login_missing_fields(self):
		"""Test login with missing required fields"""
		response = self.client.post(self.login_url, {})
		self.assertEqual(response.status_code, 400)

	def test_profile_requires_authentication(self):
		"""Test that profile endpoint requires authentication"""
		response = self.client.get(self.profile_url)
		self.assertEqual(response.status_code, 401)

	def test_profile_authenticated_user(self):
		"""Test getting profile for authenticated user"""
		user = User.objects.create_user(
			username="testuser",
			email="testuser@gmail.com",
			password="testpass123",
		)
		profile = UserProfile.objects.create(user=user, role=UserProfile.ROLE_BFP)
		token = Token.objects.create(user=user)
		
		self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
		response = self.client.get(self.profile_url)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["email"], "testuser@gmail.com")
		self.assertEqual(response.data["role"], UserProfile.ROLE_BFP)


class CameraTests(TestCase):
	"""Test Camera CRUD endpoints"""

	def setUp(self):
		self.client = APIClient()
		self.cameras_url = "/api/cameras/"
		
		# Create authenticated user
		self.user = User.objects.create_user(
			username="testuser",
			email="test@gmail.com",
			password="testpass123",
		)
		self.token = Token.objects.create(user=self.user)
		self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

	def test_list_cameras(self):
		"""Test retrieving list of cameras"""
		Camera.objects.create(
			camera_code="CAM-001",
			name="Front Gate",
			location="Main Entrance",
		)
		Camera.objects.create(
			camera_code="CAM-002",
			name="Parking Lot",
			location="North",
		)
		
		response = self.client.get(self.cameras_url)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 2)

	def test_create_camera(self):
		"""Test creating a new camera"""
		data = {
			"camera_code": "CAM-NEW",
			"name": "New Camera",
			"location": "Test Location",
			"status": Camera.STATUS_ONLINE,
		}
		response = self.client.post(self.cameras_url, data)
		
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["name"], "New Camera")
		self.assertTrue(Camera.objects.filter(camera_code="CAM-NEW").exists())

	def test_create_camera_duplicate_code(self):
		"""Test that duplicate camera code is rejected"""
		Camera.objects.create(
			camera_code="CAM-001",
			name="Existing Camera",
			location="Test",
		)
		
		data = {
			"camera_code": "CAM-001",
			"name": "Duplicate Camera",
			"location": "Test",
		}
		response = self.client.post(self.cameras_url, data)
		
		self.assertEqual(response.status_code, 400)

	def test_retrieve_camera(self):
		"""Test retrieving a specific camera"""
		camera = Camera.objects.create(
			camera_code="CAM-001",
			name="Test Camera",
			location="Test Location",
		)
		
		response = self.client.get(f"{self.cameras_url}{camera.id}/")
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["camera_code"], "CAM-001")

	def test_update_camera(self):
		"""Test updating a camera"""
		camera = Camera.objects.create(
			camera_code="CAM-001",
			name="Old Name",
			location="Old Location",
		)
		
		data = {
			"camera_code": "CAM-001",
			"name": "Updated Name",
			"location": "Updated Location",
			"status": Camera.STATUS_OFFLINE,
		}
		response = self.client.put(f"{self.cameras_url}{camera.id}/", data)
		
		self.assertEqual(response.status_code, 200)
		camera.refresh_from_db()
		self.assertEqual(camera.name, "Updated Name")

	def test_delete_camera(self):
		"""Test deleting a camera"""
		camera = Camera.objects.create(
			camera_code="CAM-001",
			name="Camera to Delete",
			location="Test",
		)
		
		response = self.client.delete(f"{self.cameras_url}{camera.id}/")
		
		self.assertEqual(response.status_code, 204)
		self.assertFalse(Camera.objects.filter(id=camera.id).exists())

	def test_camera_list_requires_authentication(self):
		"""Test that unauthenticated users cannot access cameras"""
		self.client.credentials()  # Clear credentials
		response = self.client.get(self.cameras_url)
		self.assertEqual(response.status_code, 401)


class IncidentTests(TestCase):
	"""Test Incident CRUD endpoints"""

	def setUp(self):
		self.client = APIClient()
		self.incidents_url = "/api/incidents/"
		
		# Create authenticated user
		self.user = User.objects.create_user(
			username="testuser",
			email="test@gmail.com",
			password="testpass123",
		)
		self.token = Token.objects.create(user=self.user)
		self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
		
		# Create test camera
		self.camera = Camera.objects.create(
			camera_code="CAM-001",
			name="Test Camera",
			location="Test Location",
		)

	def test_list_incidents(self):
		"""Test retrieving list of incidents"""
		Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Zone A",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			camera=self.camera,
			reported_by=self.user,
		)
		Incident.objects.create(
			incident_code="INC-002",
			incident_type=Incident.TYPE_GAS,
			location="Zone B",
			detection_method=Incident.METHOD_CAMERA_AI,
			camera=self.camera,
			reported_by=self.user,
		)
		
		response = self.client.get(self.incidents_url)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 2)

	def test_create_incident(self):
		"""Test creating a new incident"""
		data = {
			"incident_code": "INC-NEW",
			"incident_type": Incident.TYPE_FIRE,
			"location": "Test Zone",
			"detection_method": Incident.METHOD_HEAT_SENSOR,
			"camera": self.camera.id,
		}
		response = self.client.post(self.incidents_url, data)
		
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["incident_code"], "INC-NEW")
		self.assertEqual(response.data["reported_by"], self.user.id)  # Should auto-set

	def test_create_incident_duplicate_code(self):
		"""Test that duplicate incident code is rejected"""
		Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Test",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			camera=self.camera,
			reported_by=self.user,
		)
		
		data = {
			"incident_code": "INC-001",
			"incident_type": Incident.TYPE_GAS,
			"location": "Test",
			"detection_method": Incident.METHOD_CAMERA_AI,
			"camera": self.camera.id,
		}
		response = self.client.post(self.incidents_url, data)
		
		self.assertEqual(response.status_code, 400)

	def test_retrieve_incident(self):
		"""Test retrieving a specific incident"""
		incident = Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Zone A",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			camera=self.camera,
			reported_by=self.user,
		)
		
		response = self.client.get(f"{self.incidents_url}{incident.id}/")
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["incident_code"], "INC-001")

	def test_update_incident(self):
		"""Test updating an incident"""
		incident = Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Zone A",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			status=Incident.STATUS_OPEN,
			camera=self.camera,
			reported_by=self.user,
		)
		
		data = {
			"incident_code": "INC-001",
			"incident_type": Incident.TYPE_FIRE,
			"location": "Zone A",
			"detection_method": Incident.METHOD_HEAT_SENSOR,
			"status": Incident.STATUS_RESOLVED,
			"camera": self.camera.id,
			"notes": "Fire was extinguished.",
		}
		response = self.client.put(f"{self.incidents_url}{incident.id}/", data)
		
		self.assertEqual(response.status_code, 200)
		incident.refresh_from_db()
		self.assertEqual(incident.status, Incident.STATUS_RESOLVED)

	def test_delete_incident(self):
		"""Test deleting an incident"""
		incident = Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Zone A",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			camera=self.camera,
			reported_by=self.user,
		)
		
		response = self.client.delete(f"{self.incidents_url}{incident.id}/")
		
		self.assertEqual(response.status_code, 204)
		self.assertFalse(Incident.objects.filter(id=incident.id).exists())

	def test_incident_list_requires_authentication(self):
		"""Test that unauthenticated users cannot access incidents"""
		self.client.credentials()  # Clear credentials
		response = self.client.get(self.incidents_url)
		self.assertEqual(response.status_code, 401)


class SystemOverviewTests(TestCase):
	"""Test system overview endpoint"""

	def setUp(self):
		self.client = APIClient()
		self.overview_url = "/api/system/overview/"
		
		# Create authenticated user
		self.user = User.objects.create_user(
			username="testuser",
			email="test@gmail.com",
			password="testpass123",
		)
		self.token = Token.objects.create(user=self.user)
		self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

	def test_system_overview_requires_authentication(self):
		"""Test that overview endpoint requires authentication"""
		self.client.credentials()  # Clear credentials
		response = self.client.get(self.overview_url)
		self.assertEqual(response.status_code, 401)

	def test_system_overview_empty(self):
		"""Test overview with no data"""
		response = self.client.get(self.overview_url)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["camera_count"], 0)
		self.assertEqual(response.data["incident_count"], 0)
		self.assertEqual(response.data["open_incidents"], 0)

	def test_system_overview_with_data(self):
		"""Test overview with cameras and incidents"""
		# Create cameras
		Camera.objects.create(camera_code="CAM-001", name="Camera 1", location="Loc 1")
		Camera.objects.create(camera_code="CAM-002", name="Camera 2", location="Loc 2")
		
		# Create incidents with different statuses
		camera = Camera.objects.first()
		Incident.objects.create(
			incident_code="INC-001",
			incident_type=Incident.TYPE_FIRE,
			location="Zone A",
			detection_method=Incident.METHOD_HEAT_SENSOR,
			status=Incident.STATUS_OPEN,
			camera=camera,
			reported_by=self.user,
		)
		Incident.objects.create(
			incident_code="INC-002",
			incident_type=Incident.TYPE_GAS,
			location="Zone B",
			detection_method=Incident.METHOD_CAMERA_AI,
			status=Incident.STATUS_INVESTIGATING,
			camera=camera,
			reported_by=self.user,
		)
		Incident.objects.create(
			incident_code="INC-003",
			incident_type=Incident.TYPE_SMOKE,
			location="Zone C",
			detection_method=Incident.METHOD_MANUAL,
			status=Incident.STATUS_RESOLVED,
			camera=camera,
			reported_by=self.user,
		)
		
		response = self.client.get(self.overview_url)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["camera_count"], 2)
		self.assertEqual(response.data["incident_count"], 3)
		self.assertEqual(response.data["open_incidents"], 2)  # OPEN + INVESTIGATING
