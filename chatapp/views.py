from django.shortcuts import render
from django.http import JsonResponse
from .clients.qna_client import consult_qna
from .clients.luis_client import luis_analyze

def index(request):
    return render(request, 'index.html')

def ask_question(request):
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if not question:
            return JsonResponse({"error": "No se ha proporcionado ninguna consulta."}, status=400)

        session = request.session

        # Si existe una operación en curso y el usuario escribe "cancelar", se anula la operación.
        if session.get("intent") and question.lower() == "cancelar":
            session.pop("intent", None)
            session.pop("entities", None)
            return JsonResponse({"answer": "Operación cancelada. \n\n¿Necesitas ayuda con otra cosa?"})

        # Analizamos la consulta con LUIS
        analysis_result = luis_analyze(question)
        new_intent = analysis_result.get("top_intent")
        confidence = analysis_result.get("confidence", 0)
        entities = analysis_result.get("entities", [])

        # Lista de tallas válidas para evitar confundirlas con productos
        valid_sizes = {"XS", "S", "M", "L", "XL", "XXL"}

        # Recuperamos la intención y entidades previas en sesión (para mantener el flujo waterfall)
        prev_intent = session.get("intent")
        session_entities = session.get("entities", {})

        # Si ya hay una intención en curso, mantenemos el contexto a menos que se detecte (con alta confianza)
        # un cambio de intención.
        if prev_intent:
            session["intent"] = prev_intent
        else:
            session["intent"] = new_intent

        # Extraer entidades relevantes según lo que devuelve LUIS
        nuevo_producto = next((e["text"] for e in entities if e["category"] == "Producto"), None)
        nueva_talla = next((e["text"] for e in entities if e["category"] == "Talla"), None)
        nuevo_numero = next((e["text"] for e in entities if e["category"] == "NumeroPedido"), None)

        # Si se detecta un producto pero resulta ser una talla (por pertenecer a valid_sizes), se descarta.
        if nuevo_producto and nuevo_producto in valid_sizes:
            nuevo_producto = None

        # Actualizamos el contexto en sesión si se han detectado nuevos valores
        if nuevo_producto:
            session_entities["Producto"] = nuevo_producto
        if nueva_talla:
            session_entities["Talla"] = nueva_talla
        if nuevo_numero:
            session_entities["NumeroPedido"] = nuevo_numero

        session["entities"] = session_entities

        # Procesamos la intención activa (ya sea la recién detectada o la que estaba en curso)
        intent = session.get("intent")
        response = ""

        if intent == "CambioProducto":
            producto = session_entities.get("Producto")
            talla = session_entities.get("Talla")
            if producto and talla:
                # Se tienen todos los datos: se finaliza el proceso.
                response = (f"Genial! Vamos a cambiar tu {producto} por una talla {talla}. "
                            "Acude a la tienda o al depósito más cercano para hacer efectiva la devolución 😁.\n\n"
                            "¿Necesitas ayuda con otra cosa?")
                session.pop("entities", None)
                session.pop("intent", None)
            else:
                # Faltan datos: se pregunta al usuario según lo que no se tenga.
                if not producto and not talla:
                    response = ("Para cambiar de producto, necesito que me indiques el producto que deseas cambiar "
                                "y la talla que necesitas.")
                elif not producto:
                    response = "Para continuar con el cambio, necesito que me indiques qué producto deseas cambiar."
                elif not talla:
                    response = f"Para cambiar tu {producto}, necesito que me indiques la talla que deseas."
                    
        elif intent == "DevolucionProducto":
            producto = session_entities.get("Producto")
            if producto:
                response = (f"😰 Ups, sentimos que tengas que devolver tu {producto}. "
                            "Puedes acercarte a nuestra tienda o a tu depósito más cercano.\n\n"
                            "¿Necesitas ayuda con otra cosa?")
                session.pop("entities", None)
                session.pop("intent", None)
            else:
                response = ("Para proceder con la devolución, necesito que me indiques qué producto deseas devolver.")
                
        elif intent == "EstadoDevolucion":
            numero_pedido = session_entities.get("NumeroPedido")
            if numero_pedido:
                # Se valida que el número de pedido contenga solo dígitos.
                if numero_pedido.strip().isdigit():
                    response = (f"El estado de tu devolución con número {numero_pedido} está actualmente en proceso.\n\n"
                                "¿Necesitas ayuda con otra cosa?")
                    session.pop("entities", None)
                    session.pop("intent", None)
                else:
                    response = ("El número de pedido debe contener solo números. "
                                "Por favor, ingresa un número válido o escribe 'cancelar' para anular la operación.")
            else:
                response = ("Para verificar el estado de tu devolución, por favor proporciona el número de pedido "
                            "(solo números).")
                
        elif intent == "ConsultaPoliticas":
            # Se responde directamente usando el cliente QnA.
            response = consult_qna(question)
            # Se limpia el contexto.
            session.pop("entities", None)
            session.pop("intent", None)
            return JsonResponse(response)
        
        elif intent == "None":
            session.pop("entities", None)
            session.pop("intent", None)
            response = "Lo sentimos, No tenemos respuesta para eso 😢"
            
        else:
            response = "No entendí bien tu solicitud, ¿podrías reformularla?"
            # Se limpia el contexto en caso de intención desconocida.
            session.pop("entities", None)
            session.pop("intent", None)

        return JsonResponse({"answer": response})
        
    return JsonResponse({"error": "Solicitud inválida"}, status=400)
