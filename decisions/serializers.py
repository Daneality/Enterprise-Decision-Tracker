from rest_framework import serializers
from decisions.models import Decision, Evaluation

class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer for evaluation"""

    class Meta:
        model = Evaluation
        fields = ['goal_met', 'comments', 'evaluated_at']

class DecisionSerializer(serializers.ModelSerializer):
    """Serializer for decision"""

    evaluation = EvaluationSerializer(read_only=True)

    class Meta:
        model = Decision
        fields = ['id', 'title', 'description', 'measurable_goal', 'status', 'created_at', 'updated_at', 'evaluation']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DecisionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating decision"""

    class Meta:
        model = Decision
        fields = ['title', 'description', 'measurable_goal', 'status']

class EvaluationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating evaluation"""    

    class Meta:
        model = Evaluation
        fields = ['goal_met', 'comments']
