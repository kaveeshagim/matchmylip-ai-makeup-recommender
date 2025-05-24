from flask import Blueprint, request, jsonify
from controllers.analyzer import analyze_image

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "No image uploaded"}), 400

    result = analyze_image(image)
    return jsonify(result)