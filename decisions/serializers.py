from rest_framework import serializers
from decisions.models import Decision, Evaluation

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['goal_met', 'comments', 'evaluated_at']

class DecisionSerializer(serializers.ModelSerializer):
    evaluation = EvaluationSerializer(read_only=True)

    class Meta:
        model = Decision
        fields = ['id', 'title', 'description', 'measurable_goal', 'status', 'created_at', 'updated_at', 'evaluation']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DecisionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Decision
        fields = ['title', 'description', 'measurable_goal', 'status']

class EvaluationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = ['goal_met', 'comments']