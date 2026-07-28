import re
from django.shortcuts import render, redirect, get_object_or_404
from .models import Persona, Competencia
from groq import Groq
from django.conf import settings

CASOS_PRACTICOS = {
    "Lógica de programación y desarrollo": "Durante el despliegue de un módulo importante en producción, el sistema presenta un error inesperado que detiene el servicio. El cliente está molesto y el equipo de desarrollo no logra ponerse de acuerdo sobre la causa raíz del fallo. ¿Qué acciones inmediatas tomarías para solucionar la contingencia, mantener la comunicación adecuada y prevenir que vuelva a ocurrir?",
    "Trabajo en equipo y colaboración": "Un integrante del equipo no ha entregado sus tareas a tiempo, lo que retrasa la entrega final del proyecto. El resto del equipo está molesto. ¿Cómo manejarías esta situación para cumplir con el entregable sin generar un ambiente destructivo?",
    "Comunicación asertiva": "Debes explicarle a un cliente no técnico que la funcionalidad que solicitó tomará el doble de tiempo del estimado debido a problemas de arquitectura. ¿Cómo le comunicarías esta noticia manteniendo su confianza?",
    "Resolución de problemas técnicos": "Una base de datos de producción presenta tiempos de respuesta extremadamente lentos y las peticiones web están dando tiempo de espera agotado (timeout). ¿Cuál sería tu metodología paso a paso para diagnosticar y solucionar el problema?",
    "Orientación al cliente y servicio": "Un usuario reporta muy frustrado que una función clave de la aplicación no funciona como esperaba y exige una solución inmediata. ¿Cómo gestionarías su reclamo y qué seguimiento le darías?"
}


def registrar_persona(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        lista_competencias = request.POST.getlist('competencias')

        if len(lista_competencias) < 3 or len(lista_competencias) > 5:
            return render(request, 'competencias/registro.html', {
                'error': 'Debes seleccionar entre 3 y 5 competencias.'
            })

        # Obtenemos o creamos la persona mediante su Email
        persona, creada = Persona.objects.get_or_create(email=email, defaults={'nombre': nombre})
        
        if not creada:
            persona.nombre = nombre
            persona.save()

        # 1. ELIMINAMOS las competencias que el usuario NO seleccionó en esta ocasión
        persona.competencia_set.exclude(nombre__in=lista_competencias).delete()

        # 2. PROCESAMOS únicamente las competencias seleccionadas (3 a 5)
        for comp_nombre in lista_competencias:
            comp_obj, comp_creada = Competencia.objects.get_or_create(
                persona=persona,
                nombre=comp_nombre,
                defaults={'nivel_inicial': 20, 'nivel_final': 0}
            )
            # Si la competencia ya existía previamente y ya tenía un puntaje final,
            # actualizamos su nivel_inicial con el nivel_final anterior (para comparar Antes vs Después)
            if not comp_creada and comp_obj.nivel_final > 0:
                comp_obj.nivel_inicial = comp_obj.nivel_final
                comp_obj.save()

        return redirect('evaluar_caso', persona_id=persona.id)

    return render(request, 'competencias/registro.html')


def evaluar_caso(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)
    # Aquí ahora solo se obtendrán las competencias que se seleccionaron en el registro (3 a 5)
    competencias_persona = persona.competencia_set.all()

    if request.method == 'POST':
        groq_key = getattr(settings, 'GROQ_API_KEY', None)
        resultados_evaluacion = []

        for comp in competencias_persona:
            respuesta_usuario = request.POST.get(f'respuesta_{comp.id}', '').strip()
            caso_texto = CASOS_PRACTICOS.get(comp.nombre, "Describe cómo abordarías una contingencia en esta competencia.")

            puntaje_extraido = 0

            if groq_key and respuesta_usuario:
                try:
                    client = Groq(api_key=groq_key)
                    prompt = f"""
                    Actúa como un evaluador técnico y pedagógico experto.
                    
                    Competencia: {comp.nombre}
                    Caso práctico: {caso_texto}
                    Respuesta del estudiante: {respuesta_usuario}

                    Responde STRICTAMENTE con este formato:
                    PUNTAJE: [número de 1 a 100]
                    LO QUE HIZO BIEN: [puntos clave]
                    LO QUE FALTÓ: [aspectos a mejorar]
                    RECOMENDACIÓN FINAL: [párrafo sugerencia]
                    """

                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5,
                    )
                    evaluacion_texto = completion.choices[0].message.content

                    # Extraemos el número del PUNTAJE mediante Expresiones Regulares
                    coincidencia = re.search(r'PUNTAJE:\s*(\d+)', evaluacion_texto)
                    if coincidencia:
                        puntaje_extraido = int(coincidencia.group(1))

                except Exception as e:
                    evaluacion_texto = f"Error al evaluar esta competencia: {str(e)}"
            else:
                evaluacion_texto = "No se recibió respuesta o falta la API Key."

            # Guardamos de forma permanente la respuesta y el nuevo puntaje obtenido
            comp.ultima_respuesta = respuesta_usuario
            comp.ultimo_feedback = evaluacion_texto
            comp.nivel_final = puntaje_extraido
            comp.save()

            resultados_evaluacion.append({
                'competencia': comp.nombre,
                'caso': caso_texto,
                'respuesta': respuesta_usuario,
                'evaluacion': evaluacion_texto,
                'puntaje': puntaje_extraido
            })

        return render(request, 'competencias/resultado.html', {
            'persona': persona,
            'resultados': resultados_evaluacion
        })

    # Petición GET
    items_evaluacion = []
    for comp in competencias_persona:
        caso = CASOS_PRACTICOS.get(comp.nombre, "Describe cómo resolverías un problema práctico en esta área.")
        items_evaluacion.append({
            'competencia': comp,
            'caso_texto': caso
        })

    return render(request, 'competencias/evaluacion.html', {
        'persona': persona,
        'items_evaluacion': items_evaluacion
    })


def dashboard(request, persona_id):
    persona = get_object_or_404(Persona, id=persona_id)
    competencias = persona.competencia_set.all()

    # Cargar datos reales guardados en BD para la gráfica de Chart.js
    lista_nombres = [comp.nombre for comp in competencias]
    datos_antes = [comp.nivel_inicial for comp in competencias]
    datos_despues = [comp.nivel_final for comp in competencias]

    return render(request, 'competencias/dashboard.html', {
        'persona': persona,
        'competencias': competencias,
        'lista_nombres': lista_nombres,
        'datos_antes': datos_antes,
        'datos_despues': datos_despues,
    })
