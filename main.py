from fastapi import FastAPI, Request, HTTPException, Header
import uvicorn
import os
import subprocess
import pickle
import base64
import json
import jwt
import tempfile

app = FastAPI()

SECRET_KEY = "supersecret"
FAKE_DB = {"admin": "admin", "user": "1234"}

@app.post("/login")
def login(username: str, password: str):
    if username in FAKE_DB and FAKE_DB[username] == password:
        token = jwt.encode({"user": username}, SECRET_KEY, algorithm="HS256")
        return {"token": token}
    else:
        raise HTTPException(status_code=403, detail="Invalid credentials")

def fake_auth(auth_token: str):
    try:
        payload = jwt.decode(auth_token, options={"verify_signature": False})
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------- RCE через временный Python-файл -------------------
@app.post("/exec/file")
def exec_file(code: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    try:
        with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.getoutput(f"python {f.name}")
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/exec/file_copy")  # Дубликат
def exec_file_copy(code: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    try:
        with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            result = subprocess.getoutput(f"python {f.name}")
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------- Остальные уязвимости -------------------
@app.post("/cmd/os")
def cmd_os(cmd: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    os.system(cmd)
    return {"status": "выполнено"}

@app.post("/cmd/os_copy")
def cmd_os_copy(cmd: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    os.system(cmd)
    return {"status": "выполнено"}

@app.post("/pickle/load")
def pickle_load(data: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    try:
        decoded = base64.b64decode(data)
        obj = pickle.loads(decoded)
        return {"object": str(obj)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/file/read")
def file_read(path: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    try:
        with open(path, 'r') as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/file/read_copy")
def file_read_copy(path: str, Authorization: str = Header(None)):
    fake_auth(Authorization)
    try:
        with open(path, 'r') as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/env")
def get_env(Authorization: str = Header(None)):
    fake_auth(Authorization)
    return dict(os.environ)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
