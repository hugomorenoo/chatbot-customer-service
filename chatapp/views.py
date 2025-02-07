from django.shortcuts import render
from django.http import JsonResponse
from .clients.qna_client import consult_qna
from .clients.luis_client import luis_analyze

def index(request):
    return render(request, 'index.html')

def ask_question(request):
    if request.method == "POST":
        question = request.POST.get("question", "")
        if not question:
            return JsonResponse({"error": "No question provided"}, status=400)

        session = request.session
        
        # Analizamos la pregunta con LUIS
        analysis_result = luis_analyze(question)
        new_intent = analysis_result["top_intent"]
        entities = analysis_result.get("entities", {})

        # Lista de tallas válidas para evitar confusión con productos
        valid_sizes = {"XS", "S", "M", "L", "XL", "XXL"}

        # Recuperamos la intención previa y entidades almacenadas en sesión
        prev_intent = session.get("intent")
        session_entities = session.get("entities", {})

        # Si la intención ha cambiado, limpiamos la sesión completamente
        if prev_intent and new_intent != prev_intent and analysis_result["confidence"] > 0.95:
            session.pop("entities", None)
            session["intent"] = new_intent
        elif not prev_intent:
            session["intent"] = new_intent  # Guardamos la intención si es la primera vez

        # Función para actualizar entidades en sesión sin confusión
        def update_context(category):
            return next((e["text"] for e in entities if e["category"] == category), session_entities.get(category))

        # Manejo especial para Producto y Talla
        nuevo_producto = next((e["text"] for e in entities if e["category"] == "Producto"), None)
        nueva_talla = next((e["text"] for e in entities if e["category"] == "Talla"), None)

        # Validar si el producto detectado es una talla por error
        if nuevo_producto and nuevo_producto in valid_sizes:
            nuevo_producto = None  # Lo descartamos porque en realidad es una talla

        # Actualizar la sesión con los valores correctos
        if nuevo_producto:
            session_entities["Producto"] = nuevo_producto
        if nueva_talla:
            session_entities["Talla"] = nueva_talla

        # Guardamos los valores filtrados en sesión
        session["entities"] = session_entities

        # Procesamos la intención detectada
        if new_intent == "CambioProducto":
            producto = session_entities.get("Producto")
            talla = session_entities.get("Talla")

            if producto and talla:
                response = f"Genial! Vamos a cambiar tu {producto} por una talla {talla}. Acude a tienda o al depósito más cercano para hacer efectiva la devolución 😁.\n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al completar la tarea
            elif producto:
                response = f"Para cambiar tu {producto}, ¿puedes decirme la talla que necesitas?"
            else:
                response = "Necesitamos información sobre el producto que deseas cambiar."

        elif new_intent == "DevolucionProducto":
            producto = session_entities.get("Producto")

            if producto:
                response = f"😰 Ups, sentimos que tengas que devolver tu {producto}. Puedes acercarte a nuestra tienda o a tu depósito más cercano.\n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al completar la tarea
            else:
                response = "¿Podrías especificar qué producto deseas devolver?"

        elif new_intent == "EstadoDevolucion":
            numero_pedido = session_entities.get("NumeroPedido")

            if numero_pedido:
                response = f"El estado de tu devolución con número {numero_pedido} está actualmente en proceso.\n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al completar la tarea
            else:
                response = "Por favor, proporciona el número de pedido para verificar el estado de tu devolución."

        elif new_intent == "ConsultaPoliticas":
            response = consult_qna(question)
            return JsonResponse(response)

        else:
            response = "No entendí bien tu solicitud, ¿podrías reformularla?"

        return JsonResponse({"answer": response})

    return JsonResponse({"error": "Invalid request"}, status=400)
