from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Turma, Matricula


class MatriculaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)

    class Meta:
        model = Matricula
        fields = '__all__'


class TurmaListSerializer(serializers.ModelSerializer):
    professor_nome = serializers.CharField(source='professor_responsavel.nome', read_only=True)
    vagas_disponiveis = serializers.IntegerField(read_only=True)
    total_alunos = serializers.IntegerField(read_only=True)
    percentual_ocupacao = serializers.FloatField(read_only=True)
    dia_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = Turma
        fields = ('id', 'nome', 'faixa_etaria', 'dia_semana', 'dia_display',
                  'horario_inicio', 'capacidade', 'total_alunos',
                  'vagas_disponiveis', 'percentual_ocupacao', 'professor_nome', 'status')


class TurmaSerializer(serializers.ModelSerializer):
    vagas_disponiveis = serializers.IntegerField(read_only=True)
    total_alunos = serializers.IntegerField(read_only=True)
    matriculas = MatriculaSerializer(many=True, read_only=True)

    class Meta:
        model = Turma
        fields = '__all__'


class TurmaViewSet(viewsets.ModelViewSet):
    queryset = Turma.objects.select_related('professor_responsavel').prefetch_related('matriculas').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'faixa_etaria', 'dia_semana']
    search_fields = ['nome']

    def get_serializer_class(self):
        if self.action == 'list':
            return TurmaListSerializer
        return TurmaSerializer

    @action(detail=False, methods=['get'])
    def ativas(self, request):
        turmas = self.get_queryset().filter(status='ativa')
        serializer = TurmaListSerializer(turmas, many=True)
        return Response({'count': turmas.count(), 'results': serializer.data})

    @action(detail=True, methods=['get'])
    def matriculas(self, request, pk=None):
        turma = self.get_object()
        status = request.query_params.get('status', 'ativa')
        matriculas = turma.matriculas.filter(status=status).select_related('aluno')
        serializer = MatriculaSerializer(matriculas, many=True)
        return Response(serializer.data)
