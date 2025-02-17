# Chatbot con IA

## 🤖 Descripción
Este es un chatbot basado en inteligencia artificial diseñado para gestionar cambios y devoluciones en una tienda de ropa. Sin embargo, el código es totalmente personalizable y puede adaptarse a diferentes necesidades.

---

## ⚙️ Requisitos previos
Antes de ejecutar el proyecto, asegúrate de contar con:
- Python 3.x
- Tailwind CSS
- Django
- Una cuenta en [Azure](https://azure.microsoft.com/)
- Variables de entorno configuradas para LUIS y QnA Maker

---

## 🔍 Creación de QnA en Azure
Para la configuración de QnA en Azure, sigue las instrucciones del siguiente laboratorio:  
[Ejercicio: Creación de QnA](https://microsoftlearning.github.io/mslearn-ai-language/Instructions/Exercises/02-qna.html)

## 🔍 Creación de LUIS en Azure
Para configurar el servicio LUIS (Language Understanding Intelligent Service) en Azure, sigue los pasos descritos en este laboratorio:  
[Ejercicio: Creación de LUIS](https://microsoftlearning.github.io/mslearn-ai-language/Instructions/Exercises/03-language-understanding.html)

---

## 🌐 Intenciones implementadas
El chatbot maneja las siguientes intenciones:
- **CambioProducto**: Permite gestionar la solicitud de cambio de un producto.
- **DevoluciónProducto**: Maneja el proceso de devolución de un producto.
- **EstadoDevolución**: Consulta el estado de una devolución en curso.
- **ConsultaPolíticas**: Obtiene información sobre políticas de cambios y devoluciones (esta información se obtiene directamente desde QnA).

El tratamiento de estas intenciones se encuentra en el archivo `chatapp/views.py`, por si se desea modificar.

---

## 🔄 Ejecución del proyecto

### 1. Configuración de variables de entorno
Crear un archivo `.env` en la raíz del proyecto con la siguiente información:
```ini
AZURE_ENDPOINT = <tu_language_service_endpoint>
AZURE_KEY = <tu_language_service_key>
AZURE_PROJECT = <tu_qna_project>
AZURE_DEPLOYMENT =  <tu_qna_deployment>
```

### 2. Instalación de dependencias
Ejecuta los siguientes comandos:
```sh
pip install -r requirements.txt
```

### 3. Migraciones y ejecución del servidor Django
```sh
python manage.py migrate
python manage.py runserver
```

El chatbot estará disponible en `http://127.0.0.1:8000/`.

---

## 🎨 Personalización del frontend
Todo el contenido de la interfaz de usuario se encuentra en:  
`chatapp/templates/index.html`  
Este archivo es totalmente personalizable y estilizable según las necesidades del proyecto.
Puedes hacerlo a tu manera, por si quieres hacerlo más bonito y visual 😁

---

## 🚀 Opciones de despliegue con PythonAnywhere
Para desplegar el chatbot en PythonAnywhere:
1. Crear una cuenta en [PythonAnywhere](https://www.pythonanywhere.com/)
2. Sigue los pasos para desplegar una aplicación Django en PythonAnywhere en [este enlace](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

Para más información, revisa la [documentación oficial de PythonAnywhere](https://help.pythonanywhere.com/pages/DeployingDjango/).

---

## © Licencia
Este proyecto está bajo la licencia MIT.

## 👤 Contacto
Si tienes dudas o sugerencias, puedes contactarme en [LinkedIn](www.linkedin.com/in/hugo-moreno-fernández-561b3a2b1).

---

✨ **De Junior para Juniors** ✨

