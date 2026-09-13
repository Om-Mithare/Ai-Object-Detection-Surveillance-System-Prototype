import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    # Hugging Face Gradio spaces require the app to run on port 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
