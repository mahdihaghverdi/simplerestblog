import uvicorn

if __name__ == "__main__":
    uvicorn.run(host="0.0.0.0", port=8000, app="src.app:app", reload=True, workers=1)
