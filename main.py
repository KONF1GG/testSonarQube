from fastapi import FastAPI, HTTPException
import uvicorn 

app = FastAPI()

@app.post("/execute")
def execute_code(code: str):
    try:
        result = eval(code)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Dangerous eval() demo - POST Python code to /execute"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)