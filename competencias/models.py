from django.db import models

class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre

class Competencia(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=150)
    nivel_inicial = models.IntegerField(default=20)
    nivel_final = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} - {self.persona.nombre}"