from django.urls import path
from . import views

urlpatterns = [
    path('', views.registrar_persona, name='registrar_persona'),
    path('evaluacion/<int:persona_id>/', views.evaluar_caso, name='evaluar_caso'),
    path('dashboard/<int:persona_id>/', views.dashboard, name='dashboard'),
]