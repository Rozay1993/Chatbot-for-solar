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
#podio module
from  .pypodio2 import api as podio_api

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
#############################
client_id=os.getenv("PODIO_CLIENT_ID")
client_secret=os.getenv("PODIO_CLIENT_SECRET")
app_id=os.getenv("PODIO_APP_ID")
app_token=os.getenv("PODIO_APP_TOKEN")

podio = podio_api.OAuthAppClient(client_id,client_secret,app_id,app_token)

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

class PodioHook(APIView):
    def post(self, request, *args, **kwargs):
        request = request.data
        print(request)
        return all_path(request)
    def put(self, request, *args, **kwargs):
        request = request.data
        print(request)
        return all_path(request)
    def delete(self, request, *args, **kwargs):
        request = request.data
        print(request)
        return all_path(request)

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

def verify_hook(podio, hook_id, code):
    verify_response=podio.Hook.validate(hook_id, code)
    return Response(verify_response,status=status.HTTP_201_CREATED)

def all_path(request):
    try:
        match (request['type']):
            case 'hook.verify':
                return verify_hook(podio, hook_id=request['hook_id'], code=request['code'])
            case 'item.create':
                id="id-"+str(request['item_id'])
                item = podio.Item.find(item_id=int(id))
                new_value=all_values(item['fields'])
                set_item_to_pinecone(id, new_value)
                return Response(status=status.HTTP_201_CREATED)
            
            case 'item.update':
                id="id-"+str(request['item_id'])
                item = podio.Item.find(item_id=int(id))
                new_value=all_values(item['fields'])
                # old_id=str(new_value['PROJECT ID'])
                # old_value=get_item_from_pinecone(old_id)
                # if(old_value != False):
                #     delete_item_pinecone(old_id)
                set_item_to_pinecone(id, new_value)
                # if(old_value==False):
                #     set_item_to_pinecone(id, new_value)
                # elif(new_value['Stage'] != old_value['Stage']):
                #     print('update!')
                return Response(status=status.HTTP_201_CREATED)
            
            case 'item.delete':
                id="id-"+str(request['item_id'])
                delete_item_pinecone(id)
                return Response(status=status.HTTP_201_CREATED)
    except KeyError:
        print(KeyError)
        return Response(KeyError,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def all_values(fields):
    values={}
    for field in fields:
        match(field['type']):
            case 'app':
                values[field['label']]=''
            case 'category':
                values[field['label']]=field['values'][0]['value']['text']
            case 'date':
                values[field['label']]=field['values'][0]['start']
            case 'embed':
                values[field['label']]=field['values'][0]['embed']['url']
            case default:
                values[field['label']]=retrun_values(field)
    # print(values)
    return values

def retrun_values(field):
    print(field['label'],field['type'], ' :',field['values'][0])
    match(field['label']):
        case "Date Created" | "? Install Complete Date" | "MTRX NTP Approved Date":
            return field['values'][0]['start']
        # case "Stage" | "Warehouse territory" | "Status" | "? MTRX Install Status" | "Finance Type" | "Deal Status (Sales)" | "Welcome Call Checklist" | "HOA Approval Required?":
        #     return field['values'][0]['value']['text']
        case "Project Manager":
            return field['values'][0]['value']['name']
        case "Metrics" | "Sales Item":
            return ''
        case default:
            return field['values'][0]['value']
        
def get_item_from_pinecone(id):
    try:
        item = pine_index.fetch([id])
        print(item)
        if item is not None:
            return item[id]['metadata']
        else:
            return False
    except:
        return False
    
def set_item_to_pinecone(id, new_value):
    text= f"Now the stage for {new_value['Customer Full Name']} is {new_value['Stage']}"
    embedding = openai.Embedding.create(input=text, engine=MODEL)['data'][0]['embedding']
    pine_index.upsert(vectors=[{
        "id": id,
        'values': embedding,
        'metadata': new_value
    }],async_req=True)
    print('updated')

def delete_item_pinecone(id):
    pine_index.delete([id], delete_all=True)