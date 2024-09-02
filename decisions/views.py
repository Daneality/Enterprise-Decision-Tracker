from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from decisions.models import Decision, Evaluation
from rest_framework.exceptions import MethodNotAllowed
from decisions.serializers import DecisionSerializer, DecisionCreateUpdateSerializer, EvaluationCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DecisionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing decisions.
    """

    queryset = Decision.objects.all()
    serializer_class = DecisionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'measurable_goal']
    ordering_fields = ['title', 'status']
    ordering = ['title']

    COMMON_RESPONSES = {
        401: openapi.Response(description="Unauthorized"),
        403: openapi.Response(description="Forbidden"),
        500: openapi.Response(description="Internal Server Error"),
    }

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DecisionCreateUpdateSerializer
        return DecisionSerializer
    
    @swagger_auto_schema(
        operation_description="Create a new decision",
        responses={
            201: openapi.Response(description="Created", schema=DecisionSerializer),
            400: openapi.Response(description="Bad Request"),
            **COMMON_RESPONSES
    })
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get a specific decision",
        responses={
            404: openapi.Response(description="Not Found"),
            **COMMON_RESPONSES
    })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH', detail='Method "PATCH" not allowed.')

    @swagger_auto_schema(operation_description="Destroy a decision", responses={**COMMON_RESPONSES})
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Get a list of decisions", responses={**COMMON_RESPONSES})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a specific decision",
        responses={
            200: openapi.Response(description="OK", schema=DecisionSerializer),
            400: openapi.Response(description="Bad Request"),
            404: openapi.Response(description="Not Found"),
            **COMMON_RESPONSES
    })
    def update(self, request, *args, **kwargs):
        """
        Update a decision

        If the status of the decision is changed to 'Pending'
        or the measurable goal is changed,
        the evaluation for the decision is deleted.
        """
        decision = self.get_object()
        old_status = decision.status
        old_measurable_goal = decision.measurable_goal

        super().update(request, *args, **kwargs)

        decision.refresh_from_db()
        if self._should_delete_evaluation(old_status, old_measurable_goal, decision):
            Evaluation.objects.filter(decision=decision).delete()

        serializer = DecisionSerializer(decision)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _should_delete_evaluation(old_status, old_measurable_goal, decision):
        return (old_status != decision.status and decision.status == 'Pending') or old_measurable_goal != decision.measurable_goal

    @swagger_auto_schema(
        operation_description="Evaluate a decision",
        responses={
            201: openapi.Response(description="Created", schema=DecisionSerializer),
            400: openapi.Response(description="Bad Request"),
            404: openapi.Response(description="Not Found"),
            **COMMON_RESPONSES
        },
        request_body = EvaluationCreateSerializer
    )   
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def evaluate(self, request, pk=None):
        """
        Evaluates a decision

        Only decisions with status 'Completed' can be evaluated.
        Evaluations are unique for each decision.
        Two evaluations for the same decision are not allowed.
        """
        decision = self.get_object()
        if decision.status != 'Completed':
            return Response({"error": "Only completed decisions can be evaluated."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Evaluation.objects.filter(decision=decision).exists():
            return Response({"error": "An evaluation already exists for this decision."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EvaluationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(decision=decision)
            decision.refresh_from_db()
            decision_serializer = DecisionSerializer(decision)
            return Response(decision_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
