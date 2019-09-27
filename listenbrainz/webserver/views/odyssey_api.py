import ujson
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import current_user, login_required
from listenbrainz.webserver.decorators import crossdomain
from listenbrainz.webserver.rate_limiter import ratelimit
from listenbrainz.webserver.views.api import api_bp, _parse_int_arg # yes, I am prepared to burn in hell for this. its a hack!
from listenbrainz.domain import spotify
from brainzutils import musicbrainz_db as mbdb

TEST_RECORDINGS = [
    '4b5273c8-45f2-4bea-b73c-5128cd57faa8', 
    '4c8bba36-4bc5-4ac8-b25f-b35a43a90adb', 
    'be84c6fc-738a-49bb-b9ad-56db27a9eacb', 
    '9fa30946-ef20-49f4-be76-87b3e4329eac', 
    '9420c245-10aa-43bf-a583-08f0219e5666', 
    '7054dd17-14a2-498d-a595-5ae16a8948da', 
    '522a889a-abc2-471b-9ebb-9231fc2ff4d7', 
    '62c2e20a-559e-422f-a44c-9afa7882f0c4'
]

fakeData = [
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "55b758e5-e3a4-45c1-8fce-9ca2fe393b7b",
                "rating": "",
                "recording_mbid": "",
                "release_msid": "576d1847-2c59-4280-84dc-4700093e8855",
                "source": "P",
                "track_length": "247",
                "track_number": ""
            },
            "artist_name": "Chillhop Music",
            "release_name": "Chillhop",
            "track_name": "Stan Forebee - Look Back"
        }
    },
]

@api_bp.route("/odyssey/<mbid0>/<mbid1>")
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey(mbid0, mbid1):
 
    steps = _parse_int_arg("steps")

    recordings = mbdb.get_many_recordings_by_mbid(TEST_RECORDINGS, includes=["artists"])
    current_app.logger.error(recordings)
    mogged = []
    for recording in recordings:
        mogged.append({
            "track_metadata": {
                "additional_info": {
                    "artist_msid": "55b758e5-e3a4-45c1-8fce-9ca2fe393b7b",
                    "rating": "",
                    "recording_mbid": "",
                    "release_msid": "576d1847-2c59-4280-84dc-4700093e8855",
                    "source": "P",
                    "track_length": "247",
                    "track_number": ""
                },
                "artist_name": "Chillhop Music",
                "release_name": "Chillhop",
                "track_name": "Stan Forebee - Look Back"
            }
        })

    return jsonify({'status': 'ok', 'payload': mogged})


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
