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
        
        analysis_result = luis_analyze(question)

        intent = analysis_result["top_intent"]
        entities = analysis_result.get("entities", {})

        # Recuperamos la intención previa si el usuario no especifica una nueva
        previous_intent = session.get("intent")

        # Si no se detecta una nueva intención pero hay una previa en sesión, la usamos
        if previous_intent:
            intent = previous_intent

        # Guardamos la intención en sesión para referencia futura
        session["intent"] = intent

        # Recuperamos entidades previas almacenadas en sesión
        session_entities = session.get("entities", {})

        # Función para actualizar el contexto con nuevas entidades
        def update_context(category):
            return next((e["text"] for e in entities if e["category"] == category), session_entities.get(category))

        if intent == "CambioProducto":
            producto = update_context("Producto")
            talla = update_context("Talla")

            # Guardamos el estado actualizado en sesión
            session["entities"] = {"Producto": producto, "Talla": talla}

            if producto and talla:
                response = f"Genial! Vamos a cambiar tu {producto} por una talla {talla}, acude a tienda o al depósito más cercano para hacer efectiva la devolución 😁.\n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al finalizar
            elif producto:
                response = f"Para cambiar tu {producto}, ¿puedes decirme la talla que necesitas?"
            else:
                response = "Necesitamos información sobre el producto que deseas cambiar."

        elif intent == "DevolucionProducto":
            producto = update_context("Producto")
            session["entities"] = {"Producto": producto}

            if producto:
                response = f"😰 Ups, sentimos que tengas que devolver tu {producto}.\nPara devolver el producto {producto}, puedes acercarte a nuestra tienda o a tu depósito más cercano. \n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al finalizar
            else:
                response = "¿Podrías especificar qué producto deseas devolver?"

        elif intent == "EstadoDevolucion":
            numero_pedido = update_context("NumeroPedido")
            session["entities"] = {"NumeroPedido": numero_pedido}

            if numero_pedido:
                response = f"El estado de tu devolución con número {numero_pedido} está actualmente en proceso. \n\n¿Necesitas ayuda con otra cosa?"
                session.pop("entities", None)
                session.pop("intent", None)  # Limpiamos la intención al finalizar
            else:
                response = "Por favor, proporciona el número de pedido para verificar el estado de tu devolución."

        elif intent == "ConsultaPoliticas":
            response = consult_qna(question)
            return JsonResponse(response)

        else:
            response = "No entendí bien tu solicitud, ¿podrías reformularla?"

        return JsonResponse({"answer": response})

    return JsonResponse({"error": "Invalid request"}, status=400)
