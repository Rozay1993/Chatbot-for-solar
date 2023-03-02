# todo/todo_api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import os
from tqdm.auto import tqdm 
# moduld related with openai
import openai
# pinecone module
import pinecone
# read env file
from dotenv import load_dotenv
#get api key of openai from .env
load_dotenv()

pine_cone_api_key = os.getenv("PINE_CONE_API_KEY")
pine_cone_environment = os.getenv("PINE_CONE_ENVIRONMENT")
print("pine_cone_api_key: ",pine_cone_api_key)
print("pine_cone_environment: ",pine_cone_environment)


openai_api_key = os.getenv("OPENAI_API_KEY")
print("openai_api_key_____",openai_api_key)
openai.api_key=openai_api_key

MODEL = 'text-embedding-ada-002'

pinecone.init(api_key=pine_cone_api_key, environment=pine_cone_environment)

pine_index = pinecone.Index("podiodata")

print('start chatbot')
class Chatbot(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        chathistory =  request.data.get('chathistory'), 
        answer = answer_question(chatHistory=chathistory, debug=False)
        send_data= {}
        send_data["answer"] = answer
        return Response(send_data, status=status.HTTP_201_CREATED)

def create_context(question):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    xq  = openai.Embedding.create(input=question, engine=MODEL)['data'][0]['embedding']

    res = pine_index.query([xq], top_k=2, include_metadata=True)

    returns = []

    for match in res['matches']:
        returns.append(match['metadata']["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    model="text-davinci-003",
    chatHistory=[
        {
            "humanChat": False,
            "chatContent": "Am I allowed to publish model outputs to Twitter, without a human review?"
        }
    ],
    debug=False,
    max_tokens=1000,
    stop_sequence=None
):

    try:
        """
        Answer a question based on the most similar context from the dataframe texts
        """
        history = ""
        for chat in chatHistory[0]:
            if(chat['humanChat']):
                history+=f"\nHuman Queston: {chat['chatContent']}"
            else:
                history+=f"\nBot Answer: {chat['chatContent']}"

        question = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Check out the chat transcript below and rewrite final question as one question to include the customer's name and main details.\n---\nChatting History:\n{history}\n\n---\nNew Question: ",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )["choices"][0]["text"].strip()
        context = create_context(
            question,
        )
        # If debug, print the raw model response
        if debug:
            print("Context:\n" + context)
            print("\n\n")
        # Create a completions using the questin and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below.\"\n{context}\n\n---\n\n{history}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return "Excuse me, one problem happens to me."