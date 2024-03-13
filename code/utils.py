import requests
import time
import asyncio
import urllib3
from OpenSSL import crypto

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_audio(url, file_path, model="base"):
    """
    Send audio to the server

    Args:
    url (str): The url of the server
    file_path (str): The path to the audio file
    model (str): The model to use for transcription

    Returns:
    dict:
        Server response
        - error (str): The error message if the request failed
    """
    try:
        with open(file_path, "rb") as audio_file:
            files = {"file": audio_file}
            response = requests.post(url=url, data={
                "model": model
            }, files=files, verify=False, stream=True)
    except Exception as e:
        result = {"error": f"Failed to upload audio. Error: {e}"}
        return result
    result = None
    if response.status_code == 200:
        print("Audio uploaded successfully.")
        result = response.json()
    else:
        print(f"Failed to upload audio. Status code: {response.status_code}")
        result = {"error": f"Failed to upload audio. Status code: {response.status_code}"}
    return result

def get_text(url, id):
    """
    Get response from the server
    
    Args:
    id (str): The id of the request
    url (str): The url of the server
    
    Returns:
    dict:
        Server response
    """
    response = requests.get(url, params={"id": id}, verify=False)
    return response.json()


async def async_get_response(id, url="https://localhost:5000/transcribe", timeout=30):
    """
    Get response from the server
    
    Args:
    id (str): The id of the request
    url (str): The url of the server
    timeout (int): The timeout for the request
    
    Returns:
    dict:
        - status (str): The status of the request (success or failed)
        - text (str): The text of the request
        - time (float): The time it took to get the response
        - timeout (bool): Whether the request timed out
    """
    t = time.time()
    result = {}
    while time.time() - t < timeout:
        try:
            result = get_text(url, id)
            if "error" in result:
                result = {"status": "failed", "text": result["error"], "time": round(float(time.time() - t), 3)}
                break
            if result["status"] == "success":
                result = {"status": "success", "text": result["text"], "time": round(float(time.time() - t), 3)}
                break
        except Exception as e:
            result = {"status": "failed", "text": f"Error: {e}", "time": round(float(time.time() - t), 3)}
            break
        await asyncio.sleep(0.25)
    return result

def get_response(id, url="https://localhost:5000/transcribe", timeout=30):
    """
    Get response from the server
    
    Args:
    id (str): The id of the request
    url (str): The url of the server
    timeout (int): The timeout for the request
    
    Returns:
    dict:
        - status (str): The status of the request (success or failed)
        - text (str): The text of the request
        - time (float): The time it took to get the response
        - timeout (bool): Whether the request timed out
    """
    t = time.time()
    result = {}
    result = {"status": "failed", "text": "Request timed out"}
    while time.time() - t < timeout:
        try:
            result = get_text(url, id)
            if "error" in result:
                result = {"status": "failed", "text": result["error"]}
                break
            if result["status"] == "success":
                result = {"status": "success", "text": result["text"]}
                break
        except Exception as e:
            result = {"status": "failed", "text": f"Error: {e}"}
            break
        time.sleep(0.25)
    result["time"] = round(float(time.time() - t), 3)
    result["timeout"] = result["time"] >= timeout
    return result


def create_self_signed_cert():
    # Create a key pair
    kp = crypto.PKey()
    kp.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "FR"
    cert.get_subject().ST = "Île-de-France"
    cert.get_subject().L = "Paris"
    cert.get_subject().O = "WhisperAI"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60 * 60 * 24 * 365)  # valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(kp)
    cert.sign(kp, 'sha256')

    # Save the key and cert
    with open('./data/ssl/key.pem', 'wt') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, kp).decode('utf-8'))

    with open('./data/ssl/cert.pem', 'wt') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))

    # Save the cert as crt
    with open('./data/ssl/cert.crt', 'wt') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))

    # Create a CSR
    req = crypto.X509Req()
    req.get_subject().C = cert.get_subject().C
    req.get_subject().ST = cert.get_subject().ST
    req.get_subject().L = cert.get_subject().L
    req.get_subject().O = cert.get_subject().O
    req.get_subject().CN = cert.get_subject().CN
    req.set_pubkey(kp)
    req.sign(kp, 'sha256')

    # Save the CSR
    with open('./data/ssl/cert.csr', 'wt') as f:
        f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode('utf-8'))
    # Save the key as key
    with open('./data/ssl/cert.key', 'wt') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, kp).decode('utf-8'))
