from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "🟢 AutoSRE Environment is LIVE and ready for AI agents."}

if __name__ == "__main__":
    print("--- Booting Uvicorn Enterprise Server ---")
    uvicorn.run(app, host="0.0.0.0", port=7860)