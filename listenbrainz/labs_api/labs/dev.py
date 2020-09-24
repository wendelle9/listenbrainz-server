#!/usr/bin/env python3

from datasethoster.main import app, register_query
from api.artist_country_from_artist_mbid import ArtistCountryFromArtistMBIDQuery
from api.artist_credit_from_artist_mbid import ArtistCreditIdFromArtistMBIDQuery
from api.artist_credit_from_artist_msid import ArtistCreditIdFromArtistMSIDQuery
from api.msb_mapping_stats import MSBMappingStatsQuery
from api.recording_from_recording_mbid import RecordingFromRecordingMBIDQuery
import config

register_query(ArtistCountryFromArtistMBIDQuery())
register_query(ArtistCreditIdFromArtistMBIDQuery())
register_query(ArtistCreditIdFromArtistMSIDQuery())
register_query(MSBMappingStatsQuery())
register_query(RecordingFromRecordingMBIDQuery())

if __name__ == "__main__":
    app.config['MB_DATABASE_URI'] = config.MB_DATABASE_URI
    app.run(debug=True, port=8080, host="0.0.0.0")
