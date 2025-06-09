from datetime import datetime
from flask import render_template, request, jsonify, abort, redirect, url_for, session
from flask_login import current_user, login_required
from . import main_bp
from .. import db
from .models import ModelInfo, ClubRequest
from .perceptron import Perceptron, survey_to_features, get_club_from_index, train_perceptron

perceptron = train_perceptron()


@main_bp.route('/')
def index():
    clubs_dict = get_clubs_dict()
    clubs = []

    for slug, club_data in clubs_dict.items():
        club = club_data.copy()
        club['slug'] = slug
        clubs.append(club)

    return render_template("index.html", clubs=clubs, current_user=current_user)


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

@main_bp.route('/club-recommendation')
def club_recommendation():
    # Get the recommended club from the session
    club = session.get('recommended_club')

    # If no recommendation is found, redirect to the poll
    if not club:
        from flask import flash
        flash("Please complete the survey first to get a club recommendation.", "warning")
        return redirect(url_for('main_bp.poll'))

    return render_template('club_recommendation.html', club=club, current_user=current_user)
@main_bp.route('/poll', methods=['GET', 'POST'])
def poll():
    if request.method == 'POST':
        # Process the form data
        survey_data = {
            'enjoy_activities': request.form.get('enjoy_activities', 'false'),
            'enjoy_sports': request.form.get('enjoy_sports', 'false'),
            'enjoy_art': request.form.get('enjoy_art', 'false'),
            'enjoy_science': request.form.get('enjoy_science', 'false'),
            'enjoy_clubs': request.form.get('enjoy_clubs', 'false'),
            'enjoy_fieldtrips': request.form.get('enjoy_fieldtrips', 'false'),
            'overall_satisfied': request.form.get('overall_satisfied', 'false'),
            'more_resources': request.form.get('more_resources', 'false'),
            'recommend': request.form.get('recommend', 'false'),
            'enjoy_math': request.form.get('enjoy_math', 'false')
        }

        # Convert survey data to feature vector
        features = survey_to_features(survey_data)

        # Make prediction using the perceptron
        club_index = perceptron.predict(features)[0]

        # Get club details
        club = get_club_from_index(club_index)

        # Store the recommendation in the session
        session['recommended_club'] = club

        # Redirect to the recommendation page
        return redirect(url_for('main_bp.club_recommendation'))

    return render_template('poll.html', current_user=current_user)

@main_bp.route('/services')
def services():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/profile')
def profile():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/about')
def about():
    return render_template("about.html", current_user=current_user)

@main_bp.route('/settings')
def settings():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/products')
def products():
    return render_template("base.html", current_user=current_user)

@main_bp.route('/clubs/<club_slug>')
def club_detail(club_slug):
    clubs = get_clubs_dict()
    club = clubs.get(club_slug)

    if not club:
        abort(404)

    return render_template(
        'club_detail.html',
        club=club,
        current_user=current_user
    )
@main_bp.route('/club-requests/<club_name>')
@login_required
def club_requests(club_name):
    if current_user.role != 'developer' and current_user.role != 'teacher':
        return redirect(url_for('main_bp.index'))

    # Fetch pending requests for that club
    requests = ClubRequest.query.filter_by(club_name=club_name, status='pending').all()

    return render_template('admin/club_requests.html', requests=requests)

@main_bp.route('/admin/handle-request', methods=['POST'])
@login_required
def handle_request():
    if current_user.role != 'developer' and current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    req_id = data.get('request_id')
    action = data.get('action')

    req = ClubRequest.query.get(req_id)
    if not req:
        return jsonify({'success': False, 'message': 'Request not found'})

    if action == 'accept':
        req.status = 'accepted'
    elif action == 'decline':
        req.status = 'declined'
    else:
        return jsonify({'success': False, 'message': 'Invalid action'})

    db.session.commit()
    return jsonify({'success': True})
@main_bp.route('/join_club', methods=['POST'])
@login_required
def join_club():
    data = request.get_json()
    club_name = data.get('club_name')

    # Check if user already made a request
    existing = ClubRequest.query.filter_by(username=current_user.username, club_name=club_name, status='pending').first()
    if existing:
        return jsonify({'success': False, 'message': 'You already requested to join this club'})

    req = ClubRequest(username=current_user.username, club_name=club_name)
    db.session.add(req)
    db.session.commit()
    return jsonify({'success': True})


@main_bp.route('/view-requests')
@login_required
def view_all_requests():
    if current_user.role != 'developer' and current_user.role != 'teacher':
        return redirect(url_for('main_bp.index'))

    # Fetch all pending requests
    requests = ClubRequest.query.filter_by(status='pending').all()
    return render_template('admin/club_requests.html', requests=requests)

# Dictionary of clubs for search functionality
def get_clubs_dict():
    return {
        'chess-club': {
            'name': 'Chess Club',
            'teacher': 'Mr. Petrov',
            'image': 'chess.png',
            'description': 'Sharpen your mind with weekly chess tournaments and strategy workshops.'
        },
        'robotics': {
            'name': 'Robotics',
            'teacher': 'Ms. Dimitrova',
            'image': 'robots.png',
            'description': 'Build and program robots to compete in inter-school challenges.'
        },
        'art-club': {
            'name': 'Art Club',
            'teacher': 'Mrs. Ivanova',
            'image': 'art.png',
            'description': 'Express yourself through painting, drawing, and mixed-media crafts.'
        },
        'music-band': {
            'name': 'Music Band',
            'teacher': 'Mr. Georgiev',
            'image': 'band.png',
            'description': 'Jam out in ensemble sessions and prepare for school concerts.'
        },
        'mathletes': {
            'name': 'Mathletes',
            'teacher': 'Ms. Todorova',
            'image': 'math.png',
            'description': 'Solve challenging math problems and compete in tournaments.'
        },
        'drama-club': {
            'name': 'Drama Club',
            'teacher': 'Mr. Kolev',
            'image': 'drama.png',
            'description': 'Acting, directing, and stagecraft for upcoming plays and workshops.'
        },
        'debate-team': {
            'name': 'Debate Team',
            'teacher': 'Ms. Hristova',
            'image': 'debate.png',
            'description': 'Hone your public speaking and argument skills in mock debates.'
        },
        'coding-club': {
            'name': 'Coding Club',
            'teacher': 'Mr. Totev',
            'image': 'code.png',
            'description': 'Learn to build web and desktop applications using Python and JavaScript.'
        },
        'sports-club': {
            'name': 'Sports Club',
            'teacher': 'Mrs. Vasileva',
            'image': 'sports.png',
            'description': 'Team sports, fitness training, and inter-school matches.'
        },
    }

@main_bp.route('/search-suggestions')
def search_suggestions():
    query = request.args.get('query', '').lower()

    # If no query, return recent searches
    if not query:
        recent_searches = session.get('recent_searches', [])
        return jsonify({
            'suggestions': recent_searches[:2],
            'type': 'recent'
        })

    # Search in clubs
    clubs = get_clubs_dict()
    suggestions = []

    for slug, club in clubs.items():
        if query in club['name'].lower() or query in club['teacher'].lower():
            suggestions.append({
                'name': club['name'],
                'teacher': club['teacher'],
                'slug': slug
            })

    if not suggestions:
        return jsonify({
            'suggestions': [],
            'type': 'no_results'
        })

    return jsonify({
        'suggestions': suggestions,
        'type': 'results'
    })

@main_bp.route('/search')
def search_results():
    query = request.args.get('query', '')

    # Save search to recent searches
    if query:
        recent_searches = session.get('recent_searches', [])
        # Remove if already exists to avoid duplicates
        if query in recent_searches:
            recent_searches.remove(query)
        # Add to beginning of list
        recent_searches.insert(0, query)
        # Keep only the most recent 5 searches
        session['recent_searches'] = recent_searches[:5]

    # Search in clubs
    clubs = get_clubs_dict()
    results = []

    for slug, club in clubs.items():
        if query.lower() in club['name'].lower() or query.lower() in club['teacher'].lower():
            club_copy = club.copy()
            club_copy['slug'] = slug
            results.append(club_copy)

    return render_template(
        'search_results.html',
        query=query,
        results=results,
        current_user=current_user
    )
