from datetime import datetime
from flask import render_template, request, jsonify, abort, redirect, url_for, session, flash
from flask_login import current_user, login_required
from . import main_bp
from .. import db
from .models import ModelInfo, ClubRequest, Club, EventDetail
from .perceptron import Perceptron, survey_to_features, get_club_from_index, train_perceptron
from ..auth.models import User
from .models import ClubEvent
perceptron = train_perceptron()

@main_bp.route('/')
def index():
    clubs_dict = get_clubs_dict()
    clubs = []

    user_club_names = set()
    if current_user.is_authenticated:
        user_club_names = {club.name for club in current_user.clubs}

    for slug, club_data in clubs_dict.items():
        club = club_data.copy()
        club['slug'] = slug
        club_obj = Club.query.filter_by(name=club['name']).first()
        club['participant_count'] = club_obj.participants if club_obj else 0
        club['is_member'] = club['name'] in user_club_names
        clubs.append(club)

    return render_template("index.html", clubs=clubs, current_user=current_user)

@main_bp.route('/train-model', methods=['POST'])
def train_model():
    data = request.json
    user_id = data.get('user_id')
    modelName = data.get('modelName')

    import numpy as np
    from .perceptron import Perceptron
    X = np.array(data.get('X')) if data.get('X') else None
    y = np.array(data.get('y')) if data.get('y') else None
    if X is not None and y is not None and user_id:
        perceptron = Perceptron()
        perceptron.train(X, y)
        accuracy = perceptron.evaluate(X, y)
        perceptron.save_to_db(user_id=user_id, model_name=modelName, accuracy=accuracy)
        return jsonify({"success": True, "message": "Model trained and saved", "accuracy": accuracy})
    else:
        return jsonify({"success": False, "message": "Missing training data or user_id"}), 400


@main_bp.route('/results')
def results():
    from ..auth.models import TrainingResults
    all_results = TrainingResults.query.order_by(TrainingResults.created_at.desc()).all()
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

        # Store survey answers in session for review in services page
        session['last_survey_answers'] = survey_data

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
    survey_answers = session.get('last_survey_answers')
    recommended_club = session.get('recommended_club')
    return render_template("services.html", current_user=current_user, survey_answers=survey_answers, recommended_club=recommended_club)

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
    club_data = clubs.get(club_slug)
    if not club_data:
        abort(404)

    club = club_data.copy()
    club['slug'] = club_slug

    if not club:
        abort(404)

    club['is_member'] = False
    club_obj = Club.query.filter_by(name=club['name']).first()
    club['participant_count'] = club_obj.participants if club_obj else 0
    club['is_full'] = club['participant_count'] >= 25
    if current_user.is_authenticated:
        if club_obj and current_user in club_obj.users:
            club['is_member'] = True

    return render_template('club_detail.html', club=club, current_user=current_user)
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
    if current_user.role not in ['developer', 'teacher']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    req_id = data.get('request_id')
    action = data.get('action')

    req = ClubRequest.query.get(req_id)
    if not req:
        return jsonify({'success': False, 'message': 'Request not found'})

    if action == 'accept':
        req.status = 'accepted'
        user = User.query.filter_by(username=req.username).first()
        club = Club.query.filter_by(name=req.club_name).first()

        if user and club and user not in club.users:
            if club.participants >= 25:
                return jsonify({'success': False, 'message': 'The club is full'}), 400
            club.users.append(user)
            club.participants += 1  # ✅ Increment participant count

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
    club_slug = data.get('slug')

    club = Club.query.filter_by(slug=club_slug).first()

    if not club:
        print(club)
        return jsonify({'success': False, 'message': 'Club not found'})

    if current_user in club.users:
        return jsonify({'success': False, 'message': 'You are already a member of this club'})

    existing = ClubRequest.query.filter_by(username=current_user.username, club_name=club.name, status='pending').first()
    if existing:
        return jsonify({'success': False, 'message': 'You already requested to join this club'})

    req = ClubRequest(username=current_user.username, club_name=club.name)
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

    # If no query, return recent searches and club events for joined clubs
    if not query:
        recent_searches = session.get('recent_searches', [])
        club_events = []
        if current_user.is_authenticated:
            for club in current_user.clubs:
                events = ClubEvent.query.filter_by(club_id=club.id).order_by(ClubEvent.event_date.asc()).all()
                for event in events:
                    club_events.append({
                        'club_name': club.name,
                        'club_slug': club.slug,
                        'event_date': event.event_date.isoformat(),
                        'description': event.detail.description if event.detail else '',
                    })
        return jsonify({
            'suggestions': recent_searches[:2],
            'type': 'recent',
            'club_events': club_events
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

    # Also search for matching club events if authenticated
    club_events = []
    if current_user.is_authenticated:
        # Get all clubs (not just joined clubs) for searching events
        all_clubs = Club.query.all()
        for club in all_clubs:
            # Get events for this club
            events = ClubEvent.query.filter_by(club_id=club.id).order_by(ClubEvent.event_date.asc()).all()
            for event in events:
                # Check if the event description or club name matches the query
                event_description = event.detail.description if event.detail else ''
                if query in event_description.lower() or query in club.name.lower():
                    club_events.append({
                        'club_name': club.name,
                        'club_slug': club.slug,
                        'event_date': event.event_date.isoformat(),
                        'description': event_description,
                    })

    if not suggestions and not club_events:
        return jsonify({
            'suggestions': [],
            'type': 'no_results',
            'club_events': []
        })

    return jsonify({
        'suggestions': suggestions,
        'type': 'results',
        'club_events': club_events
    })

@main_bp.route('/search')
def search_results():
    query = request.args.get('query', '')
    if query:
        recent_searches = session.get('recent_searches', [])
        if query in recent_searches:
            recent_searches.remove(query)
        recent_searches.insert(0, query)
        session['recent_searches'] = recent_searches[:5]

    clubs = get_clubs_dict()
    results = []
    club_events_map = {}
    for slug, club in clubs.items():
        if query.lower() in club['name'].lower() or query.lower() in club['teacher'].lower():
            club_copy = club.copy()
            club_copy['slug'] = slug
            results.append(club_copy)
            # Fetch events for this club
            club_obj = Club.query.filter_by(slug=slug).first()
            if club_obj:
                events = ClubEvent.query.filter_by(club_id=club_obj.id).order_by(ClubEvent.event_date.asc()).all()
                club_events_map[slug] = [
                    {
                        'event_date': event.event_date.isoformat(),
                        'description': event.detail.description if event.detail else ''
                    } for event in events
                ]
            else:
                club_events_map[slug] = []

    return render_template(
        'search_results.html',
        query=query,
        results=results,
        club_events_map=club_events_map,
        current_user=current_user
    )


@main_bp.route('/clubs/<club_slug>/calendar')
@login_required
def club_calendar(club_slug):
    club = Club.query.filter_by(slug=club_slug).first()
    if not club:
        abort(404)

    # Show calendar only to members or teachers
    if current_user not in club.users and current_user.role != 'teacher':
        return redirect(url_for('main_bp.club_detail', club_slug=club_slug))

    return render_template('admin/club_calendar.html', club=club, current_user=current_user)


@main_bp.route('/api/club-events/<club_slug>', methods=['GET'])
@login_required
def get_club_events(club_slug):
    club = Club.query.filter_by(slug=club_slug).first()
    if not club:
        return jsonify({'success': False, 'message': 'Club not found'}), 404

    events = ClubEvent.query.filter_by(club_id=club.id).all()
    event_dates = [event.event_date.isoformat() for event in events]
    return jsonify({'success': True, 'events': event_dates})


@main_bp.route('/api/toggle-event', methods=['POST'])
@login_required
def toggle_event():
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    slug = data.get('slug')
    date_str = data.get('date')

    club = Club.query.filter_by(slug=slug).first()
    if not club:
        return jsonify({'success': False, 'message': 'Club not found'}), 404

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format'}), 400

    existing = ClubEvent.query.filter_by(club_id=club.id, event_date=date_obj).first()

    if existing:
        # Delete the associated detail if exists
        if existing.detail:
            db.session.delete(existing.detail)
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed'})
    else:
        # Create default event detail
        default_detail = EventDetail(
            description="This is a scheduled club event. Details will be updated by the teacher.",
            location="Room 101",
            start_time=datetime.strptime("15:00:00", "%H:%M:%S").time(),
            end_time=datetime.strptime("16:00:00", "%H:%M:%S").time()
        )
        db.session.add(default_detail)
        db.session.flush()  # Get ID without committing

        new_event = ClubEvent(
            club_id=club.id,
            event_date=date_obj,
            detail_id=default_detail.id
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added'})

@main_bp.route('/clubs/<slug>/event/<date>', methods=['GET', 'POST'])
@login_required
def edit_event(slug, date):
    club = Club.query.filter_by(slug=slug).first_or_404()
    event_date = datetime.strptime(date, '%Y-%m-%d').date()

    club_event = ClubEvent.query.filter_by(club_id=club.id, event_date=event_date).first()
    if not club_event:
        abort(404)

    # Create detail if not exists (teachers only)
    if not club_event.detail and current_user.role == 'teacher':
        detail = EventDetail()
        db.session.add(detail)
        db.session.flush()  # Get ID
        club_event.detail = detail
        db.session.commit()

    # 🧍‍♂️ Student view
    if current_user.role != 'teacher':
        if not club_event.detail:
            abort(404)  # No info to show
        return render_template('event_detail.html', club=club, date=date, event=club_event)

    # 👨‍🏫 Teacher view
    if request.method == 'POST':
        data = request.form
        club_event.detail.description = data.get('description', '')
        club_event.detail.location = data.get('location', '')
        club_event.detail.start_time = datetime.strptime(data.get('start_time'), '%H:%M').time()
        club_event.detail.end_time = datetime.strptime(data.get('end_time'), '%H:%M').time()

        db.session.commit()
        flash("Event updated successfully.", "success")
        return redirect(url_for('main_bp.club_calendar', club_slug=slug))

    return render_template('admin/edit_event.html', club=club, date=date, event=club_event)

@main_bp.route('/clubs/<club_slug>/participants')
@login_required
def club_participants(club_slug):
    club = Club.query.filter_by(slug=club_slug).first_or_404()
    participants = club.users
    return render_template('club_participants.html', club=club, participants=participants)

@main_bp.route('/admin/all-club-schedules')
@login_required
def all_club_schedules():
    if current_user.role not in ['developer', 'teacher']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main_bp.index'))
    clubs = Club.query.all()
    return render_template('admin/all_club_schedules.html', clubs=clubs, current_user=current_user)

@main_bp.route('/admin/perceptron-training-diagram')
@login_required
def perceptron_training_diagram():
    if current_user.role not in ['developer', 'teacher']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main_bp.index'))
    from ..auth.models import TrainingResults, User
    results = TrainingResults.query.order_by(TrainingResults.created_at.asc()).all()
    diagram_data = [
        {
            'x': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'y': result.accuracy or 0.0,
            'model': result.model_name,
            'username': User.query.get(result.user_id).username if result.user_id else 'Unknown'
        }
        for result in results
    ]
    return render_template('admin/perceptron_training_diagram.html', diagram_data=diagram_data, results=results, current_user=current_user)
