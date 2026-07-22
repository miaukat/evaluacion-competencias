from django.urls import path
from . import views

urlpatterns = [
    path('', views.registrar_persona, name='registrar_persona'),
    path('exito/', views.registro_exitoso, name='registro_exitoso'),
]