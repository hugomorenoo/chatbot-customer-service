from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from dotenv import load_dotenv
import os

load_dotenv()

ls_prediction_endpoint = os.getenv("AZURE_ENDPOINT")
ls_prediction_key = os.getenv("AZURE_KEY")

# Función para crear el cliente dentro de cada solicitud.
def create_client():
    return ConversationAnalysisClient(
        ls_prediction_endpoint, AzureKeyCredential(ls_prediction_key)
    )

def luis_analyze(question):
    result = get_result(question)
    
    top_intent = result["result"]["prediction"]["topIntent"]
    entities = result["result"]["prediction"]["entities"]
    confidence = result["result"]["prediction"]["intents"][0]["confidenceScore"]

    return {"top_intent" : top_intent, "entities": entities, "confidence": confidence}

def get_result(question):
    cls_project = 'Intents'
    deployment_slot = 'production'

    # Crear el cliente dentro del bloque with
    with create_client() as client:
        query = question
        result = client.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "es",
                        "text": query
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": cls_project,
                    "deploymentName": deployment_slot,
                    "verbose": True
                }
            }
        )
    
    return result
