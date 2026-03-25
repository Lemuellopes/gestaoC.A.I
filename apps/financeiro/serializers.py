from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from datetime import date
from decimal import Decimal
from .models import Mensalidade, Pagamento


class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'


class MensalidadeSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    valor_pendente = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)
    mes_display = serializers.CharField(source='get_mes_display', read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Mensalidade
        fields = '__all__'


class MensalidadeViewSet(viewsets.ModelViewSet):
    queryset = Mensalidade.objects.select_related('aluno').prefetch_related('pagamentos').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'mes', 'ano', 'aluno']
    search_fields = ['aluno__nome', 'aluno__matricula']
    serializer_class = MensalidadeSerializer

    @action(detail=False, methods=['get'])
    def vencidas(self, request):
        mens = self.get_queryset().filter(status='vencida').order_by('data_vencimento')
        serializer = self.get_serializer(mens, many=True)
        return Response({'count': mens.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def resumo_mes(self, request):
        hoje = date.today()
        mes = int(request.query_params.get('mes', hoje.month))
        ano = int(request.query_params.get('ano', hoje.year))
        mens = self.get_queryset().filter(mes=mes, ano=ano)
        return Response({
            'mes': mes, 'ano': ano,
            'total_mensalidades': mens.count(),
            'pagas': mens.filter(status='paga').count(),
            'pendentes': mens.filter(status='pendente').count(),
            'vencidas': mens.filter(status='vencida').count(),
            'recebido': float(mens.filter(status='paga').aggregate(t=Sum('valor_pago'))['t'] or 0),
            'a_receber': float(mens.exclude(status__in=['paga','cancelada']).aggregate(t=Sum('valor_total'))['t'] or 0),
        })

    @action(detail=False, methods=['get'])
    def resumo_ultimos_meses(self, request):
        hoje = date.today()
        resultado = []
        for i in range(5, -1, -1):
            m = hoje.month - i
            a = hoje.year
            while m <= 0:
                m += 12
                a -= 1
            mens = self.get_queryset().filter(mes=m, ano=a)
            resultado.append({
                'mes': m, 'ano': a,
                'recebido': float(mens.filter(status='paga').aggregate(t=Sum('valor_pago'))['t'] or 0),
                'total': float(mens.aggregate(t=Sum('valor_total'))['t'] or 0),
            })
        return Response(resultado)
