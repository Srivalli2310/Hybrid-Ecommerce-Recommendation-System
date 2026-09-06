import os

from flask import Flask, render_template
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {
        "status": "success",
        "message": "Hybrid E-commerce Recommendation System is running"
    }


if __name__ == "__main__":
    app.run(debug=True)