from django.shortcuts import render, redirect
from .models import Persona, Competencia

def registrar_persona(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        competencias_raw = request.POST.get('competencias', '')

        # Crear o recuperar persona
        persona, _ = Persona.objects.get_or_create(email=email, defaults={'nombre': nombre})

        # Separar por comas
        lista_competencias = [c.strip() for c in competencias_raw.split(',') if c.strip()]

        for comp_nombre in lista_competencias:
            Competencia.objects.create(
                persona=persona,
                nombre=comp_nombre
            )

        return redirect('registro_exitoso')

    return render(request, 'competencias/registro.html')

def registro_exitoso(request):
    personas = Persona.objects.prefetch_related('competencias').all()
    return render(request, 'competencias/exito.html', {'personas': personas})