from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener variables de entorno
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")
AZURE_PROJECT = os.getenv("AZURE_PROJECT")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")

client = QuestionAnsweringClient(AZURE_ENDPOINT, AzureKeyCredential(AZURE_KEY))


print(load_dotenv())

def consult_qna(question):
    output = client.get_answers(
        question=question,
        project_name=AZURE_PROJECT,
        deployment_name=AZURE_DEPLOYMENT
    )

    if output.answers[0].confidence > 0.60:
            answer = f"{output.answers[0].answer} ¿Necesitas ayuda con otra cosa?"
    else:
        answer = "Lo sentimos, no tenemos respuesta para eso 😢"

    prompts = output.answers[0].dialog.prompts

    dialog_text = []
    if prompts:
        for prompt in prompts:
            dialog_text.append(prompt.display_text)

    return {"answer": answer, "prompts" : dialog_text, "confidence": output.answers[0].confidence}