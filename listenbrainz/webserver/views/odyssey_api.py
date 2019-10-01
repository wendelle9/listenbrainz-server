import ujson
import requests
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import current_user, login_required
from listenbrainz.webserver.errors import APIInternalServerError, APINotFound, APIBadRequest
from listenbrainz.webserver.decorators import crossdomain
from listenbrainz.webserver.rate_limiter import ratelimit
from listenbrainz.webserver.views.api import api_bp, _parse_int_arg # yes, I am prepared to burn in hell for this. its a hack!
from listenbrainz.webserver.views.api_tools import is_valid_uuid
from listenbrainz.domain import spotify
from brainzutils.musicbrainz_db import recording as mb_rec
from brainzutils.musicbrainz_db.exceptions import NoDataFoundException

SIMILARITY_SERVER_URL = "http://similarity.acousticbrainz.org:8088/api/v1/path/"

@api_bp.route("/odyssey/<mbid0>/<mbid1>")
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey(mbid0, mbid1):
 
    steps = _parse_int_arg("steps")

    if not is_valid_uuid(mbid0) or not is_valid_uuid(mbid1):
        raise APIBadRequest("One or both of the recording MBIDs are invalid.")

    url = SIMILARITY_SERVER_URL + "similarity_path/" + mbid0 + "/" + mbid1 + "?metric=" + metric
    current_app.logger.error(url)

    r = requests.get(url)
    if r.status_code == 404:
        raise APINotFound("One or more of the passed MBIDs were not present on the similarity server.")

    if r.status_code != 200:
        raise APIInternalServerError("Similarity server returned error %s" % r.status_code)

    data = r.json()
    if not data:
        raise APINotFound("A path between the two given tracks could not be found.")

    recordings = mb_rec.get_many_recordings_by_mbid(data, includes=["artists"])
    mogged = []
    for mbid in recordings.keys():
        armbids = [ a['id'] for a in recordings[mbid]['artists'] ]
        arnames = [ a['name'] for a in recordings[mbid]['artists'] ]
        mogged.append({
            "track_metadata": {
                "additional_info": {
                    "artist_msid": "",
                    "rating": "",
                    "recording_mbid": mbid,
                    "release_msid": "",
                    "source": "",
                    "track_number": "",
                    "artist_mbids": armbids,
                    "artist_names": arnames,
                },
                "artist_name": recordings[mbid]['artists'][0]['name'], 
                "track_name": recordings[mbid]['name'], 
            }
        })

    return jsonify({'status': 'ok', 'payload': mogged})


@api_bp.route("/odyssey/debug/<mbid>")
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey_debug(mbid):
 
    if not is_valid_uuid(mbid):
        raise APIBadRequest("The given MBID is invalid.")

    metric = request.args.get("metric", "mfccs")
    max = int(request.args.get("max", "25"))
    current_app.logger.error(metric)
    current_app.logger.error(max)



    url = SIMILARITY_SERVER_URL + metric + "/" + mbid + "?steps=%d" % max
    current_app.logger.error(url)

    r = requests.get(url)
    if r.status_code == 404:
        raise APINotFound("The given MBID was present on the similarity server.")

    if r.status_code != 200:
        raise APIInternalServerError("Similarity server returned error %s" % r.status_code)

    data = r.json()
    current_app.logger.error(data)

    if not data:
        raise APINotFound("The similarity server returned no data.")

    while True:
        recording_ids = [ item[0] for item in data ]
        try:
            recordings = mb_rec.get_many_recordings_by_mbid(recording_ids, includes=["artists"])
            break
        except NoDataFoundException as err:
            missing = ujson.loads(str(err)[33:].replace("'", '"'))
            new_data = []
            for rec, value in data:
                if rec not in missing:
                    new_data.append((rec, value))
            data = new_data

    mogged = []
    for mbid, dist in zip(recordings.keys(), data):
        armbids = [ a['id'] for a in recordings[mbid]['artists'] ]
        arnames = [ a['name'] for a in recordings[mbid]['artists'] ]
        mogged.append({
            "track_metadata": {
                "additional_info": {
                    "artist_msid": "",
                    "rating": "",
                    "recording_mbid": mbid,
                    "release_msid": "",
                    "source": "",
                    "track_number": "",
                    "artist_mbids": armbids,
                    "artist_names": arnames,
                    "distance": dist[1],
                },
                "artist_name": recordings[mbid]['artists'][0]['name'], 
                "track_name": recordings[mbid]['name'], 
            }
        })

    return jsonify({'status': 'ok', 'payload': mogged})


odyssey_bp = Blueprint("odyssey", __name__)
@odyssey_bp.route("/", defaults={"mbid0" : "", "mbid1" : ""})
@odyssey_bp.route("/<mbid0>", defaults={"mbid1" : ""})
@odyssey_bp.route("/<mbid0>/<mbid1>")
@login_required
def odyssey(mbid0, mbid1):
    
    metric = request.args.get("metric", "mfccs")
    if mbid0 and not mbid1:
        mode = "similarity"
    else:
        mode = "odyssey"
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
        "mbid0" : mbid0,
        "mbid1" : mbid1,
        "metric" : metric,
        "metrics" : [ "mfccs", "mfccsw", "gfccs", "gfccsw", "bpm", "key", "onsetrate", "moods", "instruments", "dortmund", "rosamerica", "tzanetakis" ],
        "mode" : mode
    }

    return render_template(
        "index/odyssey.html",
        props=ujson.dumps(props),
        user=current_user,
    )

