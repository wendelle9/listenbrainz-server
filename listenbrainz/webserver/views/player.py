import uuid
import ujson
from werkzeug.exceptions import BadRequest
from flask import Blueprint, render_template, current_app, request
from flask_login import current_user, login_required
from listenbrainz.domain import spotify
from brainzutils.musicbrainz_db import recording as mb_rec
from brainzutils.musicbrainz_db.exceptions import NoDataFoundException

#{
#    "name" : "My precious playlist",
#    "description" : "A playlist made from super powerful pink unicorns. Sparkly pink unicorns.",
#    "created" : "2019-11-19T11:49:16.199744",
#    "recordings" : [
#        {
#            "mbid" : "145f5c43-0ac2-4886-8b09-63d0e92ded5d",
#            "sources" : [
#                {
#                    "uri" : "spotify:track:3Ty7OTBNSigGEpeW2PqcsC",
#                    "uri_type" : "spotify"
#                },
#                {
#                    "uri" : "https://www.youtube.com/watch?v=4qQyUi4zfDs",
#                    "uri_type" : "youtube"
#                }
#            ]
#        }
#    ]
#}

player_bp = Blueprint("player", __name__)

# This function uses the format above to parse/validate pasted data. However, we're having a hard time
# Finding a good way to POST this data into the browser... :(
def validate_playlist(playlist):
    """
        Validate the incoming playlist; be lienient in what you accept to make this as easy to use as possible.
    """

    metadata = {}
    if "name" not in playlist:
        metadata["name"] = "unknown playlist"
    else:
        metadata["name"] = playlist["name"]
    
    if "description" not in playlist:
        metadata["description"] = ""
    else:
        metadata["description"] = playlist["description"]

    if "created" not in playlist:
        playlist["created"] = ""
    else:
        metadata["created"] = playlist["created"]

    recordings = {}
    if "recordings" not in playlist:
        raise BadRequest("recordings key missing from submitted playlist. How do you expect us to do anything with that???")

    for i, recording in enumerate(playlist["recordings"]):
        if "recording_mbid" not in recording:
            raise BadRequest("recording_mbid is missing from recording #%d" % i)

        data = { "recording_mbid" : recording["recording_mbid"], "player_sources" : [] }
        if "player_sources" in recording:
            for source in recording["player_sources"]:
                if "uri" not in source:
                    raise BadRequest("The uri field must be present in a player_sources entry.")
                if "uri_type" not in source:
                    raise BadRequest("The uri_type field must be present in a player_sources entry.")

                data["player_sources"].append({ "uri" : source["uri"], "uri_type" : source["uri_type"] })

        recordings.append(data)


    return recordings, metadata


@player_bp.route("/", methods=["GET"])
@login_required
def load():
    """ 
        This player is the start of the BrainzPlayer concept where anyone (logged into LB) can post playlist
        composed of recording MBIDs and have the player attempt to make the list playable.
    """

    recording_mbids = request.args.get("recordings", [])
    lookup_recordings = recording_mbids.split(",")
    for recording in lookup_recordings:
        try:
            u = uuid.UUID(recording)
        except ValueError:
            return render_template(
                "standalone-player.html",
                error="Cannot parse recordings argument. This page needs a comma separated list of recording MBIDs in order to play those tracks."
            )

    if len(lookup_recordings) == 0:
        return render_template(
            "standalone-player.html",
            error="No or an empty recordings argument was passged to this page. This page needs a comma separated list of recording MBIDs in order to play those tracks."
        )

    name = request.args.get("name", "")
    desc = request.args.get("desc", "")
    created = request.args.get("created", "")

    metadata = {
        "name" : name, 
        "description" : desc,
        "created" : created
    }

    # lookup the metadata for posted recording ids
    lookup_recordings = recording_mbids.split(",")
    while True:
        try:
            mb_recordings = mb_rec.get_many_recordings_by_mbid(lookup_recordings, includes=["artists"])
            break
        except NoDataFoundException as err:
            missing = ujson.loads(str(err)[33:].replace("'", '"'))
            new_lookup = []
            for rec in lookup_recordings:
                if rec not in missing:
                    new_lookup.append(rec)
            lookup_recordings = new_lookup

    recordings = []
    for i, mbid in enumerate(mb_recordings.keys()):
        armbids = [ a['id'] for a in mb_recordings[mbid]['artists'] ]
        arnames = [ a['name'] for a in mb_recordings[mbid]['artists'] ]
        recordings.append({
            "track_metadata": {
                "additional_info": {
                    "artist_msid": "",
                    "rating": "",
                    "recording_mbid": mbid,
                    "artist_mbids": armbids,
                    "artist_names": arnames,
                },
                "artist_name": mb_recordings[mbid]['artists'][0]['name'],
                "track_name": mb_recordings[mbid]['name'],
            }
        })

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
        "recordings" : recordings,
        "metadata" : metadata
    }

    return render_template(
        "standalone-player.html",
        props=ujson.dumps(props),
        user=current_user,
        spotify_data=spotify_data
    )
