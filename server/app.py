from flask import Flask
from flask_cors import CORS
from routes.recommend import recommend_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(recommend_bp, url_prefix="/api")

@app.route("/")
def home():
    return "👋 Hello from MatchMyLip Backend!"

if __name__ == "__main__":
    app.run(debug=True)
