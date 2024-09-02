import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decisions.models import Decision, Evaluation
from decisions.serializers import DecisionSerializer, DecisionCreateUpdateSerializer\

@pytest.mark.django_db
class TestDecisionViewSet:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def admin_user(self, django_user_model):
        return django_user_model.objects.create_superuser(username="admin", email="admin@example.com", password="password")

    @pytest.fixture
    def normal_user(self, django_user_model):
        return django_user_model.objects.create_user(username="user", email="user@example.com", password="password")

    @pytest.fixture
    def decision_data(self):
        return {
            "title": "Test Decision",
            "description": "This is a test decision",
            "measurable_goal": "Increase revenue by 10%",
            "status": "Pending"
        }
    
    def test_list_decisions_no_auth(self, api_client):
        """Test that anyone can list decisions."""

        url = reverse("decision-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_decisions_auth(self, api_client, normal_user):
        """Test that authenticated users can list decisions."""

        url = reverse("decision-list")
        api_client.force_authenticate(user=normal_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_decisions_superuser(self, api_client, admin_user):
        """Test that superusers can list decisions."""

        url = reverse("decision-list")
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can create decisions."""

        url = reverse("decision-list")
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decision.objects.count() == 1
        assert Decision.objects.get().title == "Test Decision"
        assert Decision.objects.filter(status="Pending").exists()
    
    def test_create_decision_no_auth(self, api_client, decision_data):
        """Test that unauthenticated users cannot create decisions."""

        url = reverse("decision-list")
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Decision.objects.count() == 0

    def test_create_decision_no_status(self, api_client, decision_data, normal_user):
        """Test that when creating a decision without a status, the status defaults to "Pending"."""

        del decision_data["status"]
        url = reverse("decision-list")
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, decision_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Decision.objects.count() == 1
        assert Decision.objects.get().title == "Test Decision"
        assert Decision.objects.filter(status="Pending").exists()

    def test_retrieve_decision(self, api_client, decision_data):
        """Test that anyone can retrieve a decision."""

        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == decision_data["title"]

    def test_update_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can update decisions."""

        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        updated_data = {**decision_data, "title": "Updated Decision"}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert Decision.objects.get(pk=decision.pk).title == "Updated Decision"

    
    def test_update_decision_no_auth(self, api_client, decision_data):
        """Test that unauthenticated users cannot update decisions."""

        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        updated_data = {**decision_data, "title": "Updated Decision"}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Decision.objects.count() == 1
        assert Decision.objects.get(pk=decision.pk).title != "Updated Decision"

    def test_delete_decision(self, api_client, decision_data, normal_user):
        """Test that authenticated users can delete decisions."""

        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Decision.objects.count() == 0
    
    def test_delete_decision_no_auth(self, api_client, decision_data):
        """Test that unauthenticated users cannot delete decisions."""

        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert Decision.objects.count() == 1

    def test_update_decision_status_to_pending_deletes_evaluation(self, api_client, decision_data, normal_user):
        """Test that updating a decision"s status to "Pending" deletes its evaluation."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        Evaluation.objects.create(decision=decision, goal_met=True, comments="Good job")
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        decision_data["status"] = "Pending"
        updated_data = {**decision_data}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_update_decision_measurable_goal_deletes_evaluation(self, api_client, decision_data, normal_user):
        """Test that updating a decision"s measurable goal deletes its evaluation."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        api_client.force_authenticate(user=normal_user)
        Evaluation.objects.create(decision=decision, goal_met=True, comments="Good job")
        url = reverse("decision-detail", kwargs={"pk": decision.pk})
        decision_data["measurable_goal"] = "New goal"
        updated_data = {**decision_data}
        response = api_client.put(url, updated_data)
        assert response.status_code == status.HTTP_200_OK
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_evaluate_decision(self, api_client, admin_user, decision_data):
        """Test that superusers can evaluate completed decisions."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-evaluate", kwargs={"pk": decision.pk})
        evaluation_data = {"goal_met": True, "comments": "Great decision"}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Evaluation.objects.filter(decision=decision).exists()

    def test_evaluate_decision_without_comment(self, api_client, admin_user, decision_data):
        """Test that superusers can evaluate completed decisions without providing a comment."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-evaluate", kwargs={"pk": decision.pk})
        evaluation_data = {"goal_met": True}  # No comment provided
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Evaluation.objects.filter(decision=decision).exists()

    def test_non_admin_cannot_evaluate(self, api_client, normal_user, decision_data):
        """Test that non-superusers cannot evaluate decisions."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        url = reverse("decision-evaluate", kwargs={"pk": decision.pk})
        evaluation_data = {"goal_met": True, "comments": "Great decision"}
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Evaluation.objects.filter(decision=decision).exists()

    def test_evaluate_pending_decision_fails(self, api_client, admin_user, decision_data):
        """Test that evaluating a pending decision fails."""

        decision = Decision.objects.create(**decision_data)  # Status is "Pending" by default
        url = reverse("decision-evaluate", kwargs={"pk": decision.pk})
        evaluation_data = {"goal_met": True, "comments": "Great decision"}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Evaluation.objects.filter(decision=decision).exists()


    def test_evaluate_decision_twice_fails(self, api_client, admin_user, decision_data):
        """Test that evaluating a decision twice fails."""

        decision_data["status"] = "Completed"
        decision = Decision.objects.create(**decision_data)
        Evaluation.objects.create(decision=decision, goal_met=True, comments="First evaluation")
        url = reverse("decision-evaluate", kwargs={"pk": decision.pk})
        evaluation_data = {"goal_met": False, "comments": "Second evaluation"}
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, evaluation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Evaluation.objects.filter(decision=decision).get().comments == "First evaluation"

@pytest.mark.django_db
class TestDecisionViewSetFiltersAndPagination:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def decisions(self):
        Decision.objects.create(title="Decisions 1", description="Description 1", measurable_goal="Goal 1", status="Pending")
        Decision.objects.create(title="Decisions 2", description="Description 2", measurable_goal="Goal 2", status="Completed")
        Decision.objects.create(title="Another decision", description="Description 3", measurable_goal="Another goal", status="Pending")

    def test_filter_by_status(self, api_client, decisions):
        """Test filtering decisions by status."""
        url = reverse("decision-list")
        response = api_client.get(url, {"status": "Pending"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert all(decision["status"] == "Pending" for decision in response.data["results"])

    def test_search_by_title(self, api_client, decisions):
        """Test searching decisions by title."""
        url = reverse("decision-list")
        response = api_client.get(url, {"search": "Decisions"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]["title"] == "Decisions 1"

    def test_search_by_measurable_goal(self, api_client, decisions):
        """Test searching decisions by measurable goal."""
        url = reverse("decision-list")
        response = api_client.get(url, {"search": "Another"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["measurable_goal"] == "Another goal"

    def test_ordering(self, api_client, decisions):
        """Test ordering decisions by title."""
        url = reverse("decision-list")
        response = api_client.get(url, {"ordering": "title"})
        assert response.status_code == status.HTTP_200_OK
        titles = [decision["title"] for decision in response.data["results"]]
        assert titles == sorted(titles)

    def test_pagination(self, api_client):
        """Test pagination of decisions."""
        # Create 25 decisions
        for i in range(25):
            Decision.objects.create(title=f"Decision {i}", description=f"Description {i}", measurable_goal=f"Goal {i}", status="Pending")

        url = reverse("decision-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert len(response.data["results"]) == 10  # First page should have 10 items

        # Check second page
        response = api_client.get(url, {"page": 2})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10  # Second page should have 10 items

        # Check third page
        response = api_client.get(url, {"page": 3})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5  # Third page should have 5 items
