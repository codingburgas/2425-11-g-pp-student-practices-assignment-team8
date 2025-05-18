from datetime import datetime
from flask import render_template, request, jsonify
from flask_login import current_user
from . import main_bp
from .. import db
from .models import ModelInfo


@main_bp.route('/')
def index():
    models = [
        {"name": "Perceptron", "image": "models/Perceptron.png"},
        {"name": "Linear Regression", "image": "models/LinearRegression.png"},
        {"name": "Logistic Regression", "image": "models/LogisticRegression.png"}
    ]
    return render_template("index.html", models=models, current_user=current_user)


@main_bp.route('/train-model', methods=['POST'])
def train_model():
    data = request.json
    weights = str(data.get('weights'))
    username = data.get('username')
    modelName = data.get('modelName')

    # Create new model info record
    model_info = ModelInfo(
        weights=weights,
        username=username,
        modelName=modelName,
        accuracy=data.get('accuracy', 0.0),  # Default to 0.0 if not provided
        created_at=datetime.utcnow(),
        parameters=str(data.get('parameters', {}))  # Convert parameters to string
    )

    try:
        db.session.add(model_info)
        db.session.commit()
        return jsonify({"success": True, "message": "Model trained successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@main_bp.route('/results')
def results():
    # Get all results from the database
    all_results = ModelInfo.query.order_by(ModelInfo.created_at.desc()).all()
    return render_template(
        "results.html",
        results=all_results,
        current_user=current_user
    )
@main_bp.route('/poll', methods=['GET', 'POST'])
def poll():
    if request.method == 'POST':
        # Here you would handle the form submission
        # For now, we'll just redirect with a success message
        return render_template('index.html', message="Poll submitted successfully!")
    return render_template('poll.html', current_user=current_user)

@main_bp.route('/services')
def services():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/profile')
def profile():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/about')
def about():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/settings')
def settings():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/products')
def products():
    return render_template("base.html", current_user=current_user)
