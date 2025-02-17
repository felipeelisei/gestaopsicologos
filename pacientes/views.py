from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Pacientes, Tarefas, Consultas
from django.contrib import messages
from django.contrib.messages import constants
import json

def pacientes(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.all()
        print(pacientes)
        return render(request, 'pacientes.html', {'queixas': Pacientes.queixas_choices, 'pacientes': pacientes })
    elif request.method == "POST":
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        queixa = request.POST.get('queixa')
        foto = request.FILES.get('foto')

        if len( nome.strip() ) == 0 or not foto:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return redirect('pacientes')

        paciente = Pacientes(
            nome=nome,
            email=email,
            telefone=telefone,
            queixas=queixa,
            foto=foto
        )

        paciente.save()
        messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com suceso.')

        return redirect('pacientes')
    
    
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages import constants
from .models import Pacientes, Tarefas, Consultas

def paciente_view(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    if request.method == "GET":
        tarefas = Tarefas.objects.all()
        consultas = Consultas.objects.filter(paciente=paciente)

        # Montando os dados corretamente para o gráfico
        tuple_grafico = (
            [i.data.strftime("%Y-%m-%d") for i in consultas],  # Datas formatadas como string
            [i.humor for i in consultas]  # Mantendo os valores numéricos
        )

        # Convertendo para JSON para evitar erros de sintaxe no template
        tuple_grafico_json = json.dumps(tuple_grafico)

        return render(
            request,
            'paciente.html',
            {
                'paciente': paciente,
                'tarefas': tarefas,
                'consultas': consultas,
                'tuple_grafico_json': tuple_grafico_json
            }
        )

    elif request.method == "POST":
        humor = request.POST.get('humor')
        registro_geral = request.POST.get('registro_geral')
        video = request.FILES.get('video')
        tarefas_selecionadas = request.POST.getlist('tarefas')

        # Criando a consulta
        consulta = Consultas.objects.create(
            humor=int(humor),
            registro_geral=registro_geral,
            video=video,
            paciente=paciente
        )

        # Associando tarefas à consulta
        tarefas_objetos = Tarefas.objects.filter(id__in=tarefas_selecionadas)
        consulta.tarefas.set(tarefas_objetos)

        messages.add_message(request, constants.SUCCESS, 'Consulta cadastrada com sucesso.')

        return redirect(f'/pacientes/{id}')



def atualizar_paciente(request, id):
    pagamento_em_dia = request.POST.get('pagamento_em_dia')
    paciente = Pacientes.objects.get(id=id)

    status = True if pagamento_em_dia == 'ativo' else False
    paciente.pagamento_em_dia = status 

    paciente.save() 

    return redirect(f'/pacientes/{id}')


def excluir_consulta(request, id):
    consulta = Consultas.objects.get(id=id)
    consulta.delete()
    return redirect(f'/pacientes/{consulta.paciente.id}')


def consulta_publica(request, id):
    consulta = Consultas.objects.get(id=id)
    if not consulta.paciente.pagamento_em_dia:
        raise Http404()
    
    return render(request, 'consulta_publica.html', {'consulta': consulta})