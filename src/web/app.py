from fastapi import FastAPI

app = FastAPI(debug=True)


@app.get("/")
async def hello():
    return "Hello World"
