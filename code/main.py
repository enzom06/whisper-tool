from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import uvicorn
import dotenv
import os
import time
import uuid
import asyncio
import subprocess
import json
from typing import Optional
from utils import create_self_signed_cert

dotenv.load_dotenv()

class userRequest:
    def __init__(self):
        self.file: str = None
        self.text: str = None
        self.status: str = None
        self.model: Optional[str] = "base"  # Default model
        self.allowed_models = ["small", "medium", "large"]  # List of allowed models
        self.time_generated = time.time()
    
    def get_model_file(self, model: str) -> str:
        if model == "small":
            return "ggml-small.bin"
        elif model == "medium":
            return "ggml-medium.bin"
        else:
            return "ggml-base.bin"

    def set_model(self, model: str) -> bool:
        result = False
        if model in self.allowed_models:
            self.model = model
            result = True
            print("Invalid model. Please choose from the allowed models: small, medium, large")
        return result
    
    def __str__(self):
        return f"file: {self.file}, text: {self.text}, status: {self.status}, model: {self.model}, time_generated: {self.time_generated}"
    
    def _getJsonOutput(self):
        if os.path.exists(f"{self.file}.json"):
            with open(f"{self.file}.json", "r") as f:
                data = json.load(f)
            for text in data["transcription"]:
                self.text = text["text"]
            # maybe for each text
            self.text.strip()
            return True
        else:
            data = None
        return False
    
    def _deleteFiles(self):
        try:
            if os.path.exists(f"{self.file}.json",):
                os.remove(f"{self.file}.json",)
            if os.path.exists(f"{self.file}"):
                os.remove(f"{self.file}")
        except Exception as e:
            print(e)

    async def transcribe_file(self):
        try:
            print("transcribing", self.file, self.model)
            subprocess.run(["./code/whisper-cpp", "-m", f"./data/models/{self.get_model_file(self.model)}", "-l", "fr", "-f", self.file, "-oj"])
            self.status = "failed"
            if self._getJsonOutput():
                self.status = "success"
                result = self.text
            else:
                self.status = "failed"
                result = "transcription failed"
            self._deleteFiles()
        except Exception as e:
            result = e
            self.text = e
            print(e)
            self.status = "failed"
        self.time_generated = round(float(time.time() - self.time_generated), 3)
        return result
    

class whisper_tool:
    def __init__(self):
        self.app = FastAPI()
        if not os.path.exists("data/records"):
            os.makedirs("data/records")
        self.app.add_api_route("/", self.root)
        self.app.add_api_route("/transcribe", self.transcribe, methods=["POST"])
        self.app.add_api_route("/transcribe", self.get_transcribe, methods=["GET"])
        self.requests: dict[str, userRequest] = {}
    
    """def __del__(self):
        if os.path.exists("data/records"):
            os.rmdir("data/records")
        if self.requests:
            del self.requests"""
    
    async def root(self):
        return {
            "success": "Hello World"
            }
    
    async def transcribe(self, model: str=Form("base"), file: UploadFile = File(...)):

        # define id
        id = str(uuid.uuid4())

        start_time = time.time()
        # save file
        save_path = f"data/records/{id}.wav"
        try:
            if file.content_type == 'application/octet-stream':
                with open(save_path, 'wb') as f:
                    while chunk := await file.read(1024):
                        f.write(chunk)
            else:
                with open(save_path, 'wb') as f:
                    f.write(await file.read())
        except Exception as e:
            print(e)
            return JSONResponse({"error": f"error when save file: {e}", "id": id}, status_code=500)
        
        # transcribe
        try:
            # filename = file.filename.split(".")[1]
            self.requests[id] = userRequest()
            self.requests[id].file = f"data/records/{id}.wav"
            self.requests[id].status = "running"
            self.requests[id].set_model(model)
            # petit souci mais je vais le régler plus tard, j'ai pas le temps
            asyncio.create_task(self.requests[id].transcribe_file())
            result = {"success": "transcription in progress", "id": id}
        except Exception as e:
            # logs
            self.requests[id].status = "failed"
            print("#"*10)
            print(e)
            result = {"error": "transcription failed", "id": id}
        # logs
        print(str(time.time() - start_time))
        return JSONResponse(content=result)

    async def get_transcribe(self, id: str):
        print("id", id)
        if id in self.requests and self.requests[id].status == "success":
            result = {"text": self.requests[id].text, "status": "success", "success": "transcription success"}
            del self.requests[id]
        elif id in self.requests and self.requests[id].status == "running":
            result = {"text": "transcription in progress", "status": "running", "success": "transcription in progress"}
        elif id in self.requests and self.requests[id].status == "failed":
            result = {"text": "transcription failed", "status": "failed", "error": self.requests[id].text}
        else:
            result = {"text": "id not found", "status": "404", "error": "id not found"}
        return JSONResponse(content=result)


if __name__ == "__main__":
    create_self_signed_cert()
    #model = whisper.load_model("tiny")
    # uvicorn.run(wt.app, host="localhost", port=5000)
    #print(model.transcribe(audio="r.mp3", fp16=False))
    wt = whisper_tool()
    
    # client = CustomWSClient(os.getenv("GATEWAY_HOST"), os.getenv("GATEWAY_PORT"))
    uvicorn.run(wt.app, host=os.getenv("LAURE_SELF_HOST"), port=int(os.getenv("LAURE_SELF_PORT")), ssl_keyfile="data/ssl/cert.key", ssl_certfile="data/ssl/cert.crt")

