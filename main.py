from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import sys
import urllib.request
import uvicorn
import requests
from requests_toolbelt import MultipartEncoder
import uuid


app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)

client_id = "llfgzt4ywp" # 개발자센터에서 발급받은 Client ID 값
client_secret = "3JyuSDXPWGNyXH5mxizf5T6HFBMJp32Id0O4qWA3" # 개발자센터에서 발급받은 Client Secret 값

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/translate_en_to_kr")
async def translate_en_to_kr(input_text):
    result = translate('en', 'ko', input_text)
    return result

@app.get("/translate_kr_to_en")
async def translate_kr_to_en(input_text):
    result = translate('ko', 'en', input_text)
    return result

def translate(source, target, input_text):
    encText = urllib.parse.quote(input_text)
    # source = 원본 언어 (ko, en 등 auto 는 자동감지)
    data = "source=" + source + "&target=" + target + "&text=" + encText
    #data = "source=ko&target=en&text=" + encText
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        return response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

@app.post("/document_translate")
def document_translate(file_dir):
    data = {
    'source': 'ko',
    'target': 'en',
    'file': ('a.docx', open('a.docx', 'rb'), 'application/octet-stream', {'Content-Transfer-Encoding': 'binary'})
    }
    m = MultipartEncoder(data, boundary=uuid.uuid4())

    headers = {
    "Content-Type": m.content_type,
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret
    }

    url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/translate"
    res = requests.post(url, headers=headers, data=m.to_string())
    print(res.text)


@app.get("/document_translate_status")
def document_translate_status(request_id):
    headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret
    }

    url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/status?requestId=" + request_id
    res = requests.get(url, headers=headers)
    print(res.text)

@app.get("/download_translated_document")
def download_translated_document(request_id):
    url = "https://naveropenapi.apigw.ntruss.com/doc-trans/v1/download?requestId=" + request_id

    opener = urllib.request.build_opener()
    opener.addheaders = [('X-NCP-APIGW-API-KEY-ID', client_id), ('X-NCP-APIGW-API-KEY', client_secret)]
    urllib.request.install_opener(opener)

    urllib.request.urlretrieve(url, "b.docx")