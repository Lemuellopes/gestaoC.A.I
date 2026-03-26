from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from datetime import date
from .models import Aluno, Responsavel


class ResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        fields = '__all__'


class AlunoListSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel_principal.nome', read_only=True)
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Aluno
        fields = ('id', 'matricula', 'nome', 'faixa_etaria', 'status',
                  'data_nascimento', 'idade', 'responsavel_nome')


class AlunoSerializer(serializers.ModelSerializer):
    responsavel_principal = ResponsavelSerializer(read_only=True)
    responsavel_principal_id = serializers.PrimaryKeyRelatedField(
        queryset=Responsavel.objects.all(), source='responsavel_principal', write_only=True
    )
    idade = serializers.IntegerField(read_only=True)
    aniversario_no_mes = serializers.BooleanField(read_only=True)

    class Meta:
        model = Aluno
        fields = '__all__'


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.select_related('responsavel_principal').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'faixa_etaria']
    search_fields = ['nome', 'matricula', 'responsavel_principal__nome']
    ordering_fields = ['nome', 'data_nascimento', 'data_matricula']

    def get_serializer_class(self):
        if self.action == 'list':
            return AlunoListSerializer
        return AlunoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        data_ini = self.request.query_params.get('data_ini')
        data_fim = self.request.query_params.get('data_fim')
        if data_ini:
            qs = qs.filter(data_matricula__gte=data_ini)
        if data_fim:
            qs = qs.filter(data_matricula__lte=data_fim)
        return qs

    @action(detail=False, methods=['get'])
    def ativos(self, request):
        alunos = self.get_queryset().filter(status='ativo')
        serializer = AlunoListSerializer(alunos, many=True)
        return Response({'count': alunos.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def por_faixa_etaria(self, request):
        data = (
            self.get_queryset()
            .filter(status='ativo')
            .values('faixa_etaria')
            .annotate(total=Count('id'))
            .order_by('faixa_etaria')
        )
        return Response(list(data))

    @action(detail=False, methods=['get'])
    def aniversariantes(self, request):
        mes = request.query_params.get('mes', date.today().month)
        alunos = self.get_queryset().filter(
            status='ativo', data_nascimento__month=mes
        ).order_by('data_nascimento__day')
        serializer = AlunoListSerializer(alunos, many=True)
        return Response(serializer.data)
