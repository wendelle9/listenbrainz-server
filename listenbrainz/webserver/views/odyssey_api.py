import ujson
from flask import Blueprint, request, jsonify, current_app
from listenbrainz.webserver.decorators import crossdomain
from listenbrainz.webserver.rate_limiter import ratelimit
from listenbrainz.webserver.views.api import api_bp, _parse_int_arg # yes, I am prepared to burn in hell for this. its a hack!


@api_bp.route("/odyssey/<mbid0>/<mbid1>"):
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey(mbid0, mbid1):
 
    steps = _parse_int_arg("steps")

    return jsonify({'status': 'ok'})
