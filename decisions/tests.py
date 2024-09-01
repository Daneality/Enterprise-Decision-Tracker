import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decisions.models import Decision, Evaluation
from decisions.serializers import DecisionSerializer, DecisionCreateUpdateSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_superuser(username='admin', email='admin@example.com', password='password')

@pytest.fixture
def normal_user(django_user_model):
    return django_user_model.objects.create_user(username='user', email='user@example.com', password='password')

@pytest.fixture
def decision_data():
    return {
        'title': 'Test Decision',
        'description': 'This is a test decision',
        'measurable_goal': 'Increase revenue by 10%',
        'status': 'Pending'
    }

@pytest.mark.django_db
class TestDecisionViewSet:

    def test_list_decisions_no_auth(self, api_client):
        """Test that anyone can list decisions."""

        url = reverse('decision-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_decisions_auth(self, api_client, normal_user):
        """Test that authenticated users can list decisions."""

        url = reverse('decision-list')
        api_client.force_authenticate(user=normal_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_decisions_superuser(self, api_client, admin_user):
        """Test that superusers can list decisions."""

        url = reverse('decision-list')
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can create decisions."""

        url = reverse('decision-list')
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decision.objects.count() == 1
        assert Decision.objects.get().title == 'Test Decision'
        assert Decision.objects.filter(status='Pending').exists()
    
    def test_create_decision_no_auth(self, api_client, decision_data):
        """Test that unauthenticated users cannot create decisions."""

        url = reverse('decision-list')
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Decision.objects.count() == 0

    def test_create_decision_no_status(self, api_client, decision_data, normal_user):
        """Test that when creating a decision without a status, the status defaults to 'Pending'."""

        del decision_data['status']
        url = reverse('decision-list')
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decision.objects.count() == 1
        assert Decision.objects.get().title == 'Test Decision'
        assert Decision.objects.filter(status='Pending').exists()

    def test_retrieve_decision(self, api_client, decision_data):
        """Test that anyone can retrieve a decision."""

        decision = Decision.objects.create(**decision_data)
        url = reverse('decision-detail', kwargs={'pk': decision.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == decision_data['title']

    def test_update_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can update decisions."""

        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        url = reverse('decision-detail', kwargs={'pk': decision.pk})
        updated_data = {**decision_data, 'title': 'Updated Decision'}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert Decision.objects.get(pk=decision.pk).title == 'Updated Decision'

    def test_delete_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can delete decisions."""

        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        url = reverse('decision-detail', kwargs={'pk': decision.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Decision.objects.count() == 0

    def test_update_decision_status_to_pending_deletes_evaluation(self, api_client, decision_data, normal_user):
        """Test that updating a decision's status to 'Pending' deletes its evaluation."""

        decision_data['status'] = 'Completed'
        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        Evaluation.objects.create(decision=decision, goal_met=True, comments='Good job')
        url = reverse('decision-detail', kwargs={'pk': decision.pk})
        decision_data['status'] = 'Pending'
        updated_data = {**decision_data}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_update_decision_measurable_goal_deletes_evaluation(self, api_client, decision_data, normal_user):
        """Test that updating a decision's measurable goal deletes its evaluation."""

        decision_data['status'] = 'Completed'
        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        Evaluation.objects.create(decision=decision, goal_met=True, comments='Good job')
        url = reverse('decision-detail', kwargs={'pk': decision.pk})
        decision_data['measurable_goal'] = 'New goal'
        updated_data = {**decision_data}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_evaluate_decision(self, api_client, admin_user, decision_data):
        """Test that superusers can evaluate completed decisions."""

        decision_data['status'] = 'Completed'
        decision = Decision.objects.create(**decision_data)
        url = reverse('decision-evaluate', kwargs={'pk': decision.pk})
        evaluation_data = {'goal_met': True, 'comments': 'Great decision'}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Evaluation.objects.filter(decision=decision).exists()

    def test_non_admin_cannot_evaluate(self, api_client, normal_user, decision_data):
        """Test that non-superusers cannot evaluate decisions."""

        decision_data['status'] = 'Completed'
        decision = Decision.objects.create(**decision_data)
        url = reverse('decision-evaluate', kwargs={'pk': decision.pk})
        evaluation_data = {'goal_met': True, 'comments': 'Great decision'}
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_evaluate_pending_decision_fails(self, api_client, admin_user, decision_data):
        """Test that evaluating a pending decision fails."""

        decision = Decision.objects.create(**decision_data)  # Status is 'Pending' by default
        url = reverse('decision-evaluate', kwargs={'pk': decision.pk})
        evaluation_data = {'goal_met': True, 'comments': 'Great decision'}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Evaluation.objects.filter(decision=decision).exists()


    def test_evaluate_decision_twice_fails(self, api_client, admin_user, decision_data):
        """Test that evaluating a decision twice fails."""

        decision_data['status'] = 'Completed'
        decision = Decision.objects.create(**decision_data)
        Evaluation.objects.create(decision=decision, goal_met=True, comments='First evaluation')
        url = reverse('decision-evaluate', kwargs={'pk': decision.pk})
        evaluation_data = {'goal_met': False, 'comments': 'Second evaluation'}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Evaluation.objects.filter(decision=decision).get().comments == 'First evaluation'
