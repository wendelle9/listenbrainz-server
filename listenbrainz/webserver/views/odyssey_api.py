import ujson
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import current_user, login_required
from listenbrainz.webserver.decorators import crossdomain
from listenbrainz.webserver.rate_limiter import ratelimit
from listenbrainz.webserver.views.api import api_bp, _parse_int_arg # yes, I am prepared to burn in hell for this. its a hack!
from listenbrainz.domain import spotify

@api_bp.route("/odyssey/<mbid0>/<mbid1>")
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey(mbid0, mbid1):
 
    steps = _parse_int_arg("steps")

    return jsonify({'status': 'ok'})


odyssey_bp = Blueprint("odyssey", __name__)
@odyssey_bp.route("/")
@login_required
def odyssey():
    
    user_data = {
        "id": current_user.id,
        "name": current_user.musicbrainz_id,
        "auth_token": current_user.auth_token,
    }
    spotify_data = spotify.get_user_dict(current_user.id)

    props = {
        "user": user_data,
        "spotify": spotify_data,
        "api_url": current_app.config["API_URL"],
    }

    return render_template(
        "index/odyssey.html",
        props=ujson.dumps(props),
        user=current_user,
    )