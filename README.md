# Whisper API (LAURE tool compatible)

## Description

This is a simple transcriber API that uses whisper to transcribe audio files.

## Prerequisites

download model
you should download the model from [here](https://github.com/ggerganov/whisper.cpp/tree/master/models) and put it in the models folder.

ex: `data/models/ggml-base.bin` and `data/models/ggml-small.bin` and `data/models/ggml-medium.bin`.

# Quickstart

# Use L.A.U.R.E

*after you have modified the `.laure` file*

```bash
laure create && laure push && laure run
```

# OR (for testing and development purposes only)

## prerequisites

### In Dockerfiles add the following lines

```Dockerfile
ENV LAURE_HOST="0.0.0.0"
ENV LAURE_PORT="5000"
```

## Build the container
```bash
docker build -t testing-stt .
```

## Run the container
```bash
docker run -d -p 5000:5000 --name stt testing-stt
```

## Delete the container
```bash
docker rm -f stt
```

# API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | [/](#get) | Welcome message |
| POST | [/transcribe](#transcribe-post) | Transcribe an audio file |
| GET | [/transcribe](#transcribe-get) | Get the transcription of the audio file |

## / (GET)

Welcome message

### Return

```json
{
  "success": "Welcome to the Whisper API"
}
```

| Parameter | Type | Description |
| --- | --- | --- |
| success | boolean | The welcome message |

## /transcribe POST
Transcribe an audio file to text and return the **id** of the transcription

**application/octet-stream** is the only accepted content type for the file, *use* **stream=True** with **requests.post** to send the file if you are using requests in python

### Parameters

| Parameter | Type | Description | Additional Info |
| --- | --- | --- | --- |
| **model** | string | The model to use for the transcription | *optional*, **default** is **base** and you can use **base**/**small**/**medium** |
| **file** | file | The audio file to transcribe | |
| **secret** | string | Secret key to use the API | actually not used |

### Return

| Parameter | Type | Description | Additional Info |
| --- | --- | --- | --- |
| **id** | string | The id of the transcription | |
| **success** | boolean | True if the transcription was successful | only if success |
| **error** | string | The error message if the transcription failed | only if not success |


## /transcribe GET

Get the transcription of the audio file

### Parameters

| Parameter | Type | Description | Additional Info |
| --- | --- | --- | --- |
| **id** | string | The id of the transcription | |

### Return

| Parameter | Type | Description | Additional Info |
| --- | --- | --- | --- |
| **text** | string | The transcription of the audio file | |
| **status** | string | The status of the transcription | **success**/**running**/**failed** |
| **success** | string | Success is present if the transcription **succeeded** or is **running** | only **if not failed** |
| **error** | string | The error message if the transcription **failed** | only **if failed** |


# Examples

## Transcribe an audio file

### Request

```python
with open(file_path, "rb") as audio_file:
  files = {"file": audio_file}
  response = requests.post(url=url, data={
      "model": model
  }, files=files, verify=False, stream=True)
result = response.json()
print(result)
```

### Response

```json
{
  "id": "5f7e3b3e-3b3e-4e3b-7e3f-3b3e4e3b7e3f",
  "success": true
}
```

## Get the transcription of the audio file

### Request

```python
result = get_text(url, id)
if "error" in result:
  result = {"status": "failed", "text": result["error"]}
elif result["status"] == "success":
  result = {"status": "success", "text": result["text"]}
else:
  result = {"status": "running"}
print(result)
```

### Response

```json
{
  "text": "The transcription of the audio file",
  "status": "success",
  "success": true
}
```

# TODO before it's ready to multiple usage
- [x] Add a way to change the model
- [ ] Add a way to change the language
- [ ] maybe a ffmpeg to convert the audio file to the right format
- [ ] Add a way to get json output
- [ ] Add option like temperature, initial_prompt, ...

# References
- [I use whisper-cpp](https://github.com/ggerganov/whisper.cpp)

# License
[MIT](https://choosealicense.com/licenses/mit/)
