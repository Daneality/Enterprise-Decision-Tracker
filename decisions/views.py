from rest_framework import viewsets, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from decisions.models import Decision, Evaluation
from decisions.serializers import DecisionSerializer, DecisionCreateUpdateSerializer, EvaluationCreateSerializer

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

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DecisionCreateUpdateSerializer
        return DecisionSerializer
    
    def update(self, request, *args, **kwargs):
        decision = self.get_object()
        old_status = decision.status
        old_measurable_goal = decision.measurable_goal

        response = super().update(request, *args, **kwargs)

        # If the status of the decision has changed to 'Pending' or the measurable goal has changed, delete the existing evaluation
        decision.refresh_from_db()
        if (old_status != decision.status and decision.status == 'Pending') or old_measurable_goal != decision.measurable_goal:
            Evaluation.objects.filter(decision=decision).delete()

        return response

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def evaluate(self, request, pk=None):
        decision = self.get_object()
        # Only completed decisions can be evaluated
        if decision.status != 'Completed':
            return Response({"error": "Only completed decisions can be evaluated."}, status=status.HTTP_400_BAD_REQUEST)
        # Only one evaluation can be created for a decision
        if Evaluation.objects.filter(decision=decision).exists():
            return Response({"error": "An evaluation already exists for this decision."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EvaluationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(decision=decision)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)