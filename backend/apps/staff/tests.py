from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
from .models import Team, ShiftType, StaffMember, StaffAvailability, DailyAvailability


class TeamModelTest(TestCase):
    """Test Team model"""
    
    def setUp(self):
        self.team = Team.objects.create(
            name="Night Crew",
            code="NC",
            description="Night shift operations team",
            is_active=True
        )
    
    def test_team_creation(self):
        """Test creating a team"""
        self.assertEqual(self.team.name, "Night Crew")
        self.assertEqual(self.team.code, "NC")
        self.assertTrue(self.team.is_active)
    
    def test_team_str(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), "Night Crew")


class ShiftTypeModelTest(TestCase):
    """Test ShiftType model"""
    
    def setUp(self):
        self.team = Team.objects.create(name="Night Crew", code="NC")
        self.shift_type = ShiftType.objects.create(
            team=self.team,
            name="Day Shift",
            code="D",
            description="Day shift",
            color="#FF5733",
            is_active=True,
            sort_order=1
        )
    
    def test_shift_type_creation(self):
        """Test creating a shift type"""
        self.assertEqual(self.shift_type.name, "Day Shift")
        self.assertEqual(self.shift_type.code, "D")
        self.assertEqual(self.shift_type.team, self.team)
    
    def test_shift_type_str(self):
        """Test shift type string representation"""
        self.assertEqual(str(self.shift_type), "Night Crew - Day Shift (D)")


class StaffMemberModelTest(TestCase):
    """Test StaffMember model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='john.doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.team = Team.objects.create(name="Night Crew", code="NC")
        self.staff = StaffMember.objects.create(
            user=self.user,
            team=self.team,
            employee_id='EMP001',
            role='astronomer',
            status='active',
            hire_date=date(2020, 1, 1)
        )
    
    def test_staff_member_creation(self):
        """Test creating a staff member"""
        self.assertEqual(self.staff.employee_id, 'EMP001')
        self.assertEqual(self.staff.role, 'astronomer')
        self.assertEqual(self.staff.status, 'active')
    
    def test_full_name_property(self):
        """Test full_name property"""
        self.assertEqual(self.staff.full_name, 'John Doe')
    
    def test_is_available_property(self):
        """Test is_available property"""
        self.assertTrue(self.staff.is_available)
        self.staff.status = 'inactive'
        self.assertFalse(self.staff.is_available)


class TeamAPITest(APITestCase):
    """Test Team API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        # Clear any existing teams
        Team.objects.all().delete()
        self.team_data = {
            'name': 'Test Team',
            'code': 'TT',
            'description': 'Test team description',
            'is_active': True
        }
    
    def test_create_team(self):
        """Test creating a team via API"""
        initial_count = Team.objects.count()
        response = self.client.post('/api/staff/teams/', self.team_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), initial_count + 1)
        team = Team.objects.get(code='TT')
        self.assertEqual(team.name, 'Test Team')
    
    def test_list_teams(self):
        """Test listing teams"""
        Team.objects.create(**self.team_data)
        response = self.client.get('/api/staff/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        # Check that our test team is in the results
        self.assertTrue(any(t['code'] == 'TT' for t in data))
    
    def test_retrieve_team(self):
        """Test retrieving a single team"""
        team = Team.objects.create(**self.team_data)
        response = self.client.get(f'/api/staff/teams/{team.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Team')
    
    def test_update_team(self):
        """Test updating a team"""
        team = Team.objects.create(**self.team_data)
        updated_data = {'name': 'Updated Team', 'code': 'UT', 'is_active': False}
        response = self.client.put(f'/api/staff/teams/{team.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.name, 'Updated Team')
        self.assertFalse(team.is_active)
    
    def test_delete_team(self):
        """Test deleting a team"""
        team = Team.objects.create(**self.team_data)
        team_id = team.id
        response = self.client.delete(f'/api/staff/teams/{team_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(id=team_id).exists())


class ShiftTypeAPITest(APITestCase):
    """Test ShiftType API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        # Clear any existing data
        ShiftType.objects.all().delete()
        Team.objects.all().delete()
        
        self.team = Team.objects.create(name='Test Team', code='TT')
        self.shift_type_data = {
            'team': self.team.id,
            'name': 'Day Shift',
            'code': 'D',
            'description': 'Day shift operations',
            'color': '#FF5733',
            'is_active': True,
            'sort_order': 1
        }
    
    def test_create_shift_type(self):
        """Test creating a shift type via API"""
        initial_count = ShiftType.objects.count()
        response = self.client.post('/api/staff/shift-types/', self.shift_type_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShiftType.objects.count(), initial_count + 1)
        shift_type = ShiftType.objects.get(code='D', team=self.team)
        self.assertEqual(shift_type.name, 'Day Shift')
    
    def test_list_shift_types(self):
        """Test listing shift types"""
        # Create shift type with team instance
        shift_type_obj_data = self.shift_type_data.copy()
        shift_type_obj_data['team'] = self.team
        ShiftType.objects.create(**shift_type_obj_data)
        
        response = self.client.get('/api/staff/shift-types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        # Check that our test shift type is in the results
        self.assertTrue(any(st['code'] == 'D' for st in data))
    
    def test_filter_shift_types_by_team(self):
        """Test filtering shift types by team"""
        # Create shift type with team instance
        shift_type_obj_data = self.shift_type_data.copy()
        shift_type_obj_data['team'] = self.team
        ShiftType.objects.create(**shift_type_obj_data)
        
        response = self.client.get(f'/api/staff/shift-types/?team={self.team.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        # Check that all results belong to our team
        for st in data:
            self.assertEqual(st['team'], self.team.id)
    
    def test_update_shift_type(self):
        """Test updating a shift type"""
        # Create shift type with team instance
        shift_type_obj_data = self.shift_type_data.copy()
        shift_type_obj_data['team'] = self.team
        shift_type = ShiftType.objects.create(**shift_type_obj_data)
        
        # Update with API data (team ID)
        updated_data = self.shift_type_data.copy()
        updated_data['name'] = 'Night Shift'
        updated_data['code'] = 'N'
        response = self.client.put(f'/api/staff/shift-types/{shift_type.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        shift_type.refresh_from_db()
        self.assertEqual(shift_type.name, 'Night Shift')
    
    def test_delete_shift_type(self):
        """Test deleting a shift type"""
        # Create shift type with team instance
        shift_type_obj_data = self.shift_type_data.copy()
        shift_type_obj_data['team'] = self.team
        shift_type = ShiftType.objects.create(**shift_type_obj_data)
        
        shift_type_id = shift_type.id
        response = self.client.delete(f'/api/staff/shift-types/{shift_type_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ShiftType.objects.filter(id=shift_type_id).exists())


class StaffMemberAPITest(APITestCase):
    """Test StaffMember API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        # Clear any existing data
        StaffMember.objects.all().delete()
        User.objects.all().delete()
        Team.objects.all().delete()
        
        self.team = Team.objects.create(name='Test Team', code='TT')
        self.staff_data = {
            'user_data': {
                'username': 'john.doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            },
            'team': self.team.id,
            'employee_id': 'EMP001',
            'role': 'astronomer',
            'status': 'active',
            'hire_date': '2020-01-01'
        }
    
    def test_create_staff_member(self):
        """Test creating a staff member via API"""
        initial_staff_count = StaffMember.objects.count()
        initial_user_count = User.objects.count()
        
        response = self.client.post('/api/staff/members/', self.staff_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StaffMember.objects.count(), initial_staff_count + 1)
        self.assertEqual(User.objects.count(), initial_user_count + 1)
        
        staff = StaffMember.objects.get(employee_id='EMP001')
        self.assertEqual(staff.employee_id, 'EMP001')
        self.assertEqual(staff.user.username, 'john.doe')
    
    def test_list_staff_members(self):
        """Test listing staff members"""
        user = User.objects.create_user(username='jane.doe', email='jane@example.com')
        StaffMember.objects.create(
            user=user,
            team=self.team,
            employee_id='EMP002',
            role='astronomer',
            hire_date=date(2020, 1, 1)
        )
        response = self.client.get('/api/staff/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle both paginated and non-paginated responses
        data = response.data if isinstance(response.data, list) else response.data.get('results', response.data)
        # Check that our test staff member is in the results
        self.assertTrue(any(s['employee_id'] == 'EMP002' for s in data))
    
    def test_update_staff_member(self):
        """Test updating a staff member with user data"""
        user = User.objects.create_user(
            username='john.doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe'
        )
        staff = StaffMember.objects.create(
            user=user,
            team=self.team,
            employee_id='EMP001',
            role='astronomer',
            hire_date=date(2020, 1, 1)
        )
        
        update_data = {
            'user_data': {
                'email': 'john.new@example.com',
                'first_name': 'Johnny'
            },
            'team': self.team.id,
            'employee_id': 'EMP001',
            'role': 'telescope_operator',
            'status': 'active',
            'hire_date': '2020-01-01'
        }
        response = self.client.put(f'/api/staff/members/{staff.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        staff.refresh_from_db()
        user.refresh_from_db()
        self.assertEqual(staff.role, 'telescope_operator')
        self.assertEqual(user.first_name, 'Johnny')
        self.assertEqual(user.email, 'john.new@example.com')
    
    def test_hide_staff_member(self):
        """Test hiding a staff member by setting status to inactive"""
        user = User.objects.create_user(username='john.doe', email='john@example.com')
        staff = StaffMember.objects.create(
            user=user,
            team=self.team,
            employee_id='EMP001',
            role='astronomer',
            status='active',
            hire_date=date(2020, 1, 1)
        )
        
        update_data = {
            'user_data': {},
            'team': self.team.id,
            'employee_id': 'EMP001',
            'role': 'astronomer',
            'status': 'inactive',
            'hire_date': '2020-01-01'
        }
        response = self.client.put(f'/api/staff/members/{staff.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        staff.refresh_from_db()
        self.assertEqual(staff.status, 'inactive')
        self.assertFalse(staff.is_available)
    
    def test_delete_staff_member(self):
        """Test deleting a staff member"""
        user = User.objects.create_user(username='john.doe', email='john@example.com')
        staff = StaffMember.objects.create(
            user=user,
            team=self.team,
            employee_id='EMP001',
            role='astronomer',
            hire_date=date(2020, 1, 1)
        )
        
        staff_id = staff.id
        response = self.client.delete(f'/api/staff/members/{staff_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StaffMember.objects.filter(id=staff_id).exists())
        # Note: User object remains in the database
        self.assertTrue(User.objects.filter(username='john.doe').exists())
