#  Sistema de Evaluación de Competencias con IA

Aplicación web desarrollada en **Django (Python)** que automatiza el proceso de calificación de evaluaciones mediante el uso de Inteligencia Artificial (**Groq API**), permitiendo reducir los tiempos de espera y mantener un historial claro de la evolución de las personas a través de gráficos interactivos.

---

## ¿Qué hace la aplicación?

* **Registro y Selección:** Permite registrar al usuario y seleccionar las competencias a evaluar.
* **Evaluación Automatizada con IA:** Presenta casos prácticos donde el usuario ingresa su respuesta; la API de Groq la analiza, emite una calificación numérica, destaca sus aciertos, puntos a mejorar y sugerencias constructivas.
* **Historial y Gráficas de Evolución:** Mide el progreso del usuario comparando su nivel inicial frente al nivel logrado mediante gráficos interactivos integrados con **Chart.js**.

---

##  Tecnologías Utilizadas

* **Backend:** Python / Django
* **Base de Datos:** SQLite / Modelos de Django
* **Inteligencia Artificial:** Groq API (Modelo Llama)
* **Frontend / Visualización:** HTML, CSS, Chart.js
* **Despliegue y Archivos:** Render y Whitenoise

---

##  Instrucciones de Ejecución (Local)

Sigue estos pasos para clonar y ejecutar el proyecto en tu computadora:

### 1. Clonar el repositorio
```bash
git clone <url-de-tu-repositorio>
cd <nombre-de-la-carpeta>
