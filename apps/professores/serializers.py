from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Professor, HorarioDisponibilidade


class HorarioSerializer(serializers.ModelSerializer):
    dia_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = HorarioDisponibilidade
        fields = '__all__'


class ProfessorListSerializer(serializers.ModelSerializer):
    especialidade_display = serializers.CharField(source='get_especialidade_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tempo_de_casa = serializers.CharField(read_only=True)

    class Meta:
        model = Professor
        fields = ('id', 'nome', 'especialidade', 'especialidade_display',
                  'status', 'status_display', 'telefone', 'cidade', 'tempo_de_casa')


class ProfessorSerializer(serializers.ModelSerializer):
    horarios = HorarioSerializer(many=True, read_only=True)
    tempo_de_casa = serializers.CharField(read_only=True)
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Professor
        fields = '__all__'


class ProfessorViewSet(viewsets.ModelViewSet):
    queryset = Professor.objects.prefetch_related('horarios').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['especialidade', 'status', 'cidade', 'tipo_contrato']
    search_fields = ['nome', 'cpf', 'email', 'registro_cref']
    ordering_fields = ['nome', 'data_admissao']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfessorListSerializer
        return ProfessorSerializer

    @action(detail=False, methods=['get'])
    def ativos(self, request):
        professores = self.get_queryset().filter(status='ativo')
        serializer = ProfessorListSerializer(professores, many=True)
        return Response({'count': professores.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def por_especialidade(self, request):
        from django.db.models import Count
        data = (
            self.get_queryset()
            .filter(status='ativo')
            .values('especialidade')
            .annotate(total=Count('id'))
        )
        return Response(list(data))
