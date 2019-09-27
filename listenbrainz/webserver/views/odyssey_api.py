import ujson
from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import current_user, login_required
from listenbrainz.webserver.decorators import crossdomain
from listenbrainz.webserver.rate_limiter import ratelimit
from listenbrainz.webserver.views.api import api_bp, _parse_int_arg # yes, I am prepared to burn in hell for this. its a hack!
from listenbrainz.domain import spotify

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
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "50272b9d-14f3-4a96-9352-e03d0a2bee35",
                "artist_names": [
                    "Galaxie 500"
                ],
                "discnumber": 1,
                "duration_ms": 246666,
                "isrc": "USRY29600095",
                "release_artist_name": "Galaxie 500",
                "release_artist_names": [
                    "Galaxie 500"
                ],
                "release_msid": "fc1ebc5b-f586-4573-b567-5317e29acf67",
                "tracknumber": 5
            },
            "artist_name": "Galaxie 500",
            "release_name": "This is Our Music",
            "track_name": "Way Up High"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "69ab35a3-c877-484a-8db9-4569010e72ed",
                "release_msid": "2c60d7a3-4dad-430e-b056-02294d0400b6"
            },
            "artist_name": "Nine Inch Nails",
            "release_name": "And All That Could Have Been/Still (Two CD Deluxe Edition)",
            "track_name": "Closer [Explicit]"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "c786e16e-81de-4c96-9787-3eaa487bb6e1",
                "release_msid": "f5d0ad02-d8bb-4d7b-a25b-ae51f29ae31f"
            },
            "artist_name": "Grieves",
            "release_name": "New",
            "track_name": "Half Empty"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "f068d085-613e-44c4-b0db-3d6f5e341fc2",
                "date": "2005",
                "release_msid": "2c37ecc8-d3a6-4f40-8995-5ee5de467930",
                "totaltracks": "14",
                "tracknumber": "14"
            },
            "artist_name": "Broadcast",
            "release_name": "Tender Buttons vinyl",
            "track_name": "I Found The End"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "673c1404-9ad3-45db-ae05-e0f0f7022dc8",
                "artist_names": [
                    "Little People"
                ],
                "discnumber": 1,
                "duration_ms": 345906,
                "isrc": "GBCWH0605510",
                "release_artist_name": "Little People",
                "release_artist_names": [
                    "Little People"
                ],
                "release_msid": "5f1a23f4-9713-4613-a27f-d04afb9e55dd",
                "tracknumber": 8
            },
            "artist_name": "Little People",
            "release_name": "Mickey Mouse Operation",
            "track_name": "Idiom"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "ea0ba4a3-d77f-4e91-ab9d-178061d78df0",
                "rating": "",
                "recording_mbid": "",
                "release_msid": "d75599ee-67e9-40c5-bb41-11e65c97ab21",
                "source": "P",
                "track_length": "126",
                "track_number": ""
            },
            "artist_name": "Theodosii Spassov",
            "release_name": "Bratimene",
            "track_name": "Little Something Out Of Nothin"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "6d994548-e05d-44d0-8b4d-e64756c2c68b",
                "artist_names": [
                    "Sadistik Exekution"
                ],
                "discnumber": 1,
                "duration_ms": 304413,
                "isrc": "FR4E60101000",
                "release_artist_name": "Sadistik Exekution",
                "release_artist_names": [
                    "Sadistik Exekution"
                ],
                "release_msid": "907b97c0-30d5-42d1-a1aa-07aa7cbc89fb",
                "tracknumber": 2
            },
            "artist_name": "Sadistik Exekution",
            "release_name": "Fukk",
            "track_name": "Fukking Death"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "9d1bbdf0-298f-4875-9765-d89453ef7684",
                "artist_names": [
                    "Ghostemane",
                    "Parv0"
                ],
                "discnumber": 1,
                "duration_ms": 179200,
                "isrc": "CA5KR1935901",
                "release_artist_name": "Ghostemane, Parv0",
                "release_artist_names": [
                    "Ghostemane",
                    "Parv0"
                ],
                "release_msid": "7a4ac23f-6b48-4a51-8147-535f968c175d",
                "tracknumber": 2
            },
            "artist_name": "Ghostemane, Parv0",
            "release_name": "HUMAN ERR0R",
            "track_name": "To Whom It May Concern"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "56edfc7e-fc55-45b4-bcd9-bc91bebabff6",
                "artist_names": [
                    "Peppa Pig"
                ],
                "discnumber": 1,
                "duration_ms": 190891,
                "isrc": "CAK471903702",
                "release_artist_name": "Peppa Pig",
                "release_artist_names": [
                    "Peppa Pig"
                ],
                "release_msid": "f47f135e-5869-497f-bfc4-834235ef8e1b",
                "tracknumber": 2
            },
            "artist_name": "Peppa Pig",
            "release_name": "My First Album",
            "track_name": "Bing Bong Zoo"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "albumartist": "of Montreal",
                "artist_mbids": [
                    "8475297d-fb78-4630-8d74-9b87b6bb7cc8"
                ],
                "artist_msid": "569966c9-beb7-495f-83b0-1ea3a72468a0",
                "date": "1997-08-19",
                "discnumber": "1",
                "recording_mbid": "8c74eba3-18ba-4c38-907f-86cecb179d6b",
                "release_group_mbid": "e6ec7928-169c-3348-8103-6199f2945ac6",
                "release_mbid": "ffabf2a9-340a-3b4c-a88d-9e5f6d56d9fb",
                "release_msid": "b4af932d-3417-4263-b99a-3ce85f67cd70",
                "tags": [
                    "Lo-Fi, Indie Rock"
                ],
                "totaldiscs": "1",
                "totaltracks": "14",
                "track_mbid": "b3d98e86-b8b1-33d0-8363-7947793dcb76",
                "tracknumber": "2"
            },
            "artist_name": "of Montreal",
            "release_name": "Cherry Peel",
            "track_name": "Baby"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "d0b8ad93-5ff1-4813-8a8a-dbdf5ceb15c9",
                "release_msid": "02032e06-3cb6-4cbc-a2e0-ab6a9dea6dfe"
            },
            "artist_name": "Black Flag",
            "release_name": "My War",
            "track_name": "My War"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "7faf5c99-3b35-4718-bdab-9e24930815f8",
                "release_msid": "8c1c7572-4d0d-47d5-aa98-167044863eee"
            },
            "artist_name": "Vision Éternel",
            "release_name": "Un automne en solitude",
            "track_name": "Season In Absence"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "24032f04-2f22-4756-b844-2123c6d46a3b",
                "release_msid": "a14fff39-3765-4036-887b-0f5196b16f51"
            },
            "artist_name": "Jesse McCartney",
            "release_name": "Departure - Recharged",
            "track_name": "Leavin"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "c2a16453-54f6-4d35-9779-fbd46c5eda0d",
                "artist_names": [
                    "Buchanan Brothers"
                ],
                "discnumber": 1,
                "duration_ms": 176693,
                "isrc": "USLS30700476",
                "release_artist_name": "Various Artists",
                "release_artist_names": [
                    "Various Artists"
                ],
                "release_msid": "d76dc06e-0ec1-4320-b418-06ec773910ec",
                "tracknumber": 6
            },
            "artist_name": "Buchanan Brothers",
            "release_name": "Quentin Tarantinos Once Upon a Time in Hollywood Original Motion Picture Soundtrack",
            "track_name": "Son of a Lovin Man"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "f383d612-58bf-4311-86dd-8ddbea3e61ce",
                "artist_names": [
                    "Fujitsu"
                ],
                "discnumber": 1,
                "duration_ms": 130000,
                "isrc": "TCADD1780415",
                "release_artist_name": "Fujitsu",
                "release_artist_names": [
                    "Fujitsu"
                ],
                "release_msid": "c9821f21-fab4-498f-abf9-627042d19fd7",
                "tracknumber": 1
            },
            "artist_name": "Fujitsu",
            "release_name": "Corals",
            "track_name": "Azure"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "33fd1196-00e1-46f8-8fdf-920dcd5b6405",
                "artist_names": [
                    "Thievery Corporation"
                ],
                "discnumber": 1,
                "duration_ms": 288826,
                "isrc": "USESL0003304",
                "release_artist_name": "Thievery Corporation",
                "release_artist_names": [
                    "Thievery Corporation"
                ],
                "release_msid": "95804c4b-ddb4-4fc3-8a74-589425417631",
                "tracknumber": 4
            },
            "artist_name": "Thievery Corporation",
            "release_name": "The Mirror Conspiracy",
            "track_name": "Lebanese Blonde"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "albumartist": "Secret Garden",
                "artist_mbids": [
                    "4ac60dc3-8e50-4c70-be0e-4a4a1298f7ba"
                ],
                "artist_msid": "3b559ea6-b2b2-4dea-b758-f4a6759be952",
                "date": "2002-04-22",
                "discnumber": "1",
                "isrc": "NOAMM0125100",
                "release_group_mbid": "4153ede7-7dd3-3537-87e9-08941d4303a0",
                "release_mbid": "3b64e679-9c0d-3e4a-8ada-fbcae77babbe",
                "release_msid": "7ffe9018-815a-402f-a53f-b800e300fb38",
                "totaldiscs": "1",
                "totaltracks": "12",
                "track_mbid": "6adb017e-7f79-3498-9516-329b58885ec2",
                "tracknumber": "10"
            },
            "artist_name": "Secret Garden",
            "release_name": "Once in a Red Moon",
            "track_name": "Fairytale"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "afa1780e-1194-476e-aa3a-31466ce62f2c",
                "release_msid": 'null'
            },
            "artist_name": "New Order",
            "track_name": "Restless (Extended Mix)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_mbids": [],
                "artist_msid": "3adeb5d1-4481-4411-9a22-b860b8afd1a6",
                "recording_mbid": "",
                "release_mbid": 'null',
                "release_msid": "4bff4257-c4e5-4181-8cec-42f8c9526b7a",
                "tracknumber": 0
            },
            "artist_name": "Bit Brigade",
            "release_name": "Metroid",
            "track_name": "Chozos"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "6cae618f-86ce-4a58-9cc2-a6fadeff7207",
                "release_msid": "f90c31e6-cc83-43e0-9778-6d8783ea3fe7"
            },
            "artist_name": "Jain",
            "release_name": "Zanaka - EP",
            "track_name": "Son of a Sun"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "5486cf1a-5f8c-49f3-b11d-fbe222914cdf",
                "release_msid": 'null'
            },
            "artist_name": "Nadia Ali/Avicii",
            "track_name": "Rapture (Avicii New Generation Mix)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "81ab11b2-25ea-4836-8c24-a8ba4551ce28",
                "release_msid": "b272325c-70ba-465f-bb70-a0051cfdb985"
            },
            "artist_name": "Grandson",
            "release_name": "Rock Bottom",
            "track_name": "Rock Bottom"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "eabb2cc6-b71b-4885-b097-367445cd0985",
                "artist_names": [
                    "Phil Collins"
                ],
                "discnumber": 1,
                "duration_ms": 175746,
                "isrc": "USRH11509315",
                "release_artist_name": "Phil Collins",
                "release_artist_names": [
                    "Phil Collins"
                ],
                "release_msid": "b9b7d2f8-7394-4c2b-9d93-872e2e442907",
                "tracknumber": 5
            },
            "artist_name": "Phil Collins",
            "release_name": "Hello, I Must Be Going! (Deluxe Edition)",
            "track_name": "You Cant Hurry Love - 2016 Remaster"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "371bade5-31b7-47d2-9a47-6abe32695341",
                "artist_names": [
                    "Ramin Djawadi"
                ],
                "discnumber": 1,
                "duration_ms": 228603,
                "isrc": "GB9TP1900982",
                "release_artist_name": "Ramin Djawadi",
                "release_artist_names": [
                    "Ramin Djawadi"
                ],
                "release_msid": "1c8e32ee-a1c2-4339-bc8c-1914a51f7aea",
                "tracknumber": 15
            },
            "artist_name": "Ramin Djawadi",
            "release_name": "Gears 5 (Original Soundtrack)",
            "track_name": "Azura Combat"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "d657814b-2e6a-41d1-97d0-092002a1b9b5",
                "release_msid": 'null'
            },
            "artist_name": "蘇慧倫",
            "track_name": "鸭子"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "e098cdb9-2594-4e2a-9f8e-7ae2a97d689b",
                "artist_names": [
                    "Skumring"
                ],
                "discnumber": 1,
                "duration_ms": 755542,
                "isrc": "NO2VE1501010",
                "release_artist_name": "Skumring",
                "release_artist_names": [
                    "Skumring"
                ],
                "release_msid": "0711c35d-3643-4d7d-9e5b-519ccb23efd3",
                "tracknumber": 1
            },
            "artist_name": "Skumring",
            "release_name": "De Glemte Tider (Remastered)",
            "track_name": "Søvn (Remastered)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "064d74d9-676e-4a90-aee2-44d7bf9c1c03",
                "artist_names": [
                    "Jason Derulo",
                    "David Guetta",
                    "Nicki Minaj",
                    "Willy William"
                ],
                "discnumber": 1,
                "duration_ms": 195419,
                "isrc": "USWB11801760",
                "release_artist_name": "Jason Derulo, David Guetta",
                "release_artist_names": [
                    "Jason Derulo",
                    "David Guetta"
                ],
                "release_msid": "07d01767-ce82-4f58-a927-08b4c5e5ac8a",
                "tracknumber": 1
            },
            "artist_name": "Jason Derulo, David Guetta, Nicki Minaj, Willy William",
            "release_name": "Goodbye (feat. Nicki Minaj & Willy William)",
            "track_name": "Goodbye (feat. Nicki Minaj & Willy William)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "64792cb0-f15f-4db7-830d-aada7acaf395",
                "release_msid": "b5760aa3-5952-4ef7-b5e6-ccc965abac82"
            },
            "artist_name": "ワルキューレ",
            "release_name": "ワルキューレは裏切らない",
            "track_name": "ワルキューレは裏切らない"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "5f03752a-2cd5-4b8c-b37a-9f1f18a2bea3",
                "artist_names": [
                    "Hail The Sun"
                ],
                "discnumber": 1,
                "duration_ms": 294907,
                "isrc": "US3X51839906",
                "release_artist_name": "Hail The Sun",
                "release_artist_names": [
                    "Hail The Sun"
                ],
                "release_msid": "7ee8c21d-8015-46f4-99ad-54bf2328674a",
                "tracknumber": 6
            },
            "artist_name": "Hail The Sun",
            "release_name": "Mental Knife",
            "track_name": "A Lesson in Lust"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "8ea90a77-4c0d-4339-9b6c-b3a3e4266224",
                "release_msid": "408bb964-f12d-4b46-8b20-f7c5493f88f5"
            },
            "artist_name": "Shannon Wright",
            "release_name": "Secret Blood",
            "track_name": "Chair to Room"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "ce2f6224-fd21-4217-9b4e-ca7d536cfe35",
                "release_msid": "8a837572-8f66-4158-a187-44d0ea5f3da2"
            },
            "artist_name": "Stand Atlantic",
            "release_name": "Skinny Dipping",
            "track_name": "Cigarette Kiss"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "125c7da4-a064-4f0c-ab4f-2466d13a3d06",
                "release_msid": "c54619ef-4252-4c33-b8df-907eb7505aae"
            },
            "artist_name": "Kazumi Totaka",
            "release_name": "Animal Crossing: New Leaf",
            "track_name": "1 AM"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "ebdbb21f-f9b8-4e9d-ba2d-27dc4a14a72c",
                "release_msid": "98aea68e-b30d-4218-b449-48655afbbde1"
            },
            "artist_name": "Air",
            "release_name": "Premiers Symptômes",
            "track_name": "Le Soleil est près de moi"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "e4e134e3-deb5-42e4-9162-976575ff8c9a",
                "release_msid": "0b951849-0de2-46c3-8620-2b680b19ccc8"
            },
            "artist_name": "Alec Benjamin",
            "release_name": "Let Me Down Slowly (feat. Alessia Cara) - Single",
            "track_name": "Let Me Down Slowly (feat. Alessia Cara)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "2a58f66a-f172-4662-aacb-4c9a39036584",
                "release_msid": "15e4ead3-94ab-4054-bd21-769d5db53f67"
            },
            "artist_name": "The Lemonheads",
            "release_name": "Its A Shame About Ray (Expanded Edition)",
            "track_name": "Rockin Stroll (Remastered)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "e3162dce-ec1e-441e-a034-9fe7b898b5ae",
                "release_msid": "0b8c0773-3118-4c59-ad82-18648dc5aad7"
            },
            "artist_name": "Terraphobia",
            "release_name": "Evilution",
            "track_name": "Doctor Death"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "4d186f48-18ab-43cd-8103-429f8640983f",
                "artist_names": [
                    "Stupeflip"
                ],
                "discnumber": 1,
                "duration_ms": 184266,
                "isrc": "FR0Z21600160",
                "release_artist_name": "Stupeflip",
                "release_artist_names": [
                    "Stupeflip"
                ],
                "release_msid": "84784a03-5881-43f6-ac9f-88837400e89d",
                "tracknumber": 16
            },
            "artist_name": "Stupeflip",
            "release_name": "Stup Virus",
            "track_name": "Crou Anthem"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "debb6edf-e7db-4f31-bb4b-0584e2b3be94",
                "release_msid": "f5fcf6cc-22aa-4934-bf44-09e8f6ec9cee"
            },
            "artist_name": "Julien Mier",
            "release_name": "Untangle the Roots",
            "track_name": "New Eyes"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "f068d085-613e-44c4-b0db-3d6f5e341fc2",
                "date": "2005",
                "release_msid": "2c37ecc8-d3a6-4f40-8995-5ee5de467930",
                "totaltracks": "14",
                "tracknumber": "13"
            },
            "artist_name": "Broadcast",
            "release_name": "Tender Buttons vinyl",
            "track_name": "You And Me In Time"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "f69942be-bccd-44eb-8962-2e5025507196",
                "release_msid": "f8a36f48-65d3-4369-9c2d-f641f17f458b"
            },
            "artist_name": "Slowdive",
            "release_name": "Souvlaki",
            "track_name": "Melon Yellow"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "7f91fe11-ab5a-4355-8f70-93ac75b84287",
                "artist_names": [
                    "Ebb & Flod"
                ],
                "discnumber": 1,
                "duration_ms": 175150,
                "isrc": "SE5Q51827568",
                "release_artist_name": "Ebb & Flod",
                "release_artist_names": [
                    "Ebb & Flod"
                ],
                "release_msid": "6d2548a2-d623-49ef-aa66-1edfe1e0c722",
                "tracknumber": 4
            },
            "artist_name": "Ebb & Flod",
            "release_name": "Moonrise",
            "track_name": "October Skies"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "f7d59008-1490-44a6-a6da-9a965108526c",
                "artist_names": [
                    "Powerwolf"
                ],
                "discnumber": 1,
                "duration_ms": 385400,
                "isrc": "USMBR1108256",
                "release_artist_name": "Powerwolf",
                "release_artist_names": [
                    "Powerwolf"
                ],
                "release_msid": "d22d863c-2238-4ee8-a415-f62a094f4632",
                "tracknumber": 11
            },
            "artist_name": "Powerwolf",
            "release_name": "Blood of the Saints",
            "track_name": "Ira Sancti (When the Saints Are Going Wild)"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "9b962ba7-3838-4d81-8246-6af5980960f6",
                "release_msid": "39991a4c-ddc6-4d73-977b-969156609173"
            },
            "artist_name": "Gacha Bakradze",
            "release_name": "Anjunadeep 09",
            "track_name": "Contactless"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "b3f8f33e-aa8e-461e-b789-bcfeb39bb08c",
                "artist_names": [
                    "Josef K"
                ],
                "discnumber": 1,
                "duration_ms": 127226,
                "isrc": "GBHBR0405452",
                "release_artist_name": "Josef K",
                "release_artist_names": [
                    "Josef K"
                ],
                "release_msid": "e31f7f57-4492-4a32-a902-fb748babbeef",
                "tracknumber": 2
            },
            "artist_name": "Josef K",
            "release_name": "Sorry for Laughing",
            "track_name": "Heads Watch"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "7faf5c99-3b35-4718-bdab-9e24930815f8",
                "release_msid": "8c1c7572-4d0d-47d5-aa98-167044863eee"
            },
            "artist_name": "Vision Éternel",
            "release_name": "Un Automne En Solitude",
            "track_name": "Season In Absence"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_mbid": "b7539c32-53e7-4908-bda3-81449c367da6",
                "artist_msid": "e29fd013-45c0-4edd-abe2-8635fdd0502a",
                "recording_mbid": "8aa577ef-2e66-498c-8d94-86f96645847d",
                "release_mbid": "7fde29c4-4230-4680-9667-359d33aed38d",
                "release_msid": "e3105e6c-4f01-4af8-8ca8-ca9e7410a713"
            },
            "artist_name": "Lana Del Rey",
            "release_name": "Norman Fucking Rockwell!",
            "track_name": "Norman Fucking Rockwell"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "0d5aad58-2e55-4e84-870b-99edbf958fe6",
                "artist_names": [
                    "Sum 41"
                ],
                "discnumber": 1,
                "duration_ms": 230184,
                "isrc": "USHR21910803",
                "release_artist_name": "Sum 41",
                "release_artist_names": [
                    "Sum 41"
                ],
                "release_msid": "ea6754c1-d2b5-4f01-ae14-76b606fe28ec",
                "tracknumber": 3
            },
            "artist_name": "Sum 41",
            "release_name": "Order In Decline",
            "track_name": "The New Sensation"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "2c0211f0-450d-4882-8e97-e7b47593c475",
                "artist_names": [
                    "Izïa"
                ],
                "discnumber": 1,
                "duration_ms": 202106,
                "isrc": "FRUM71900870",
                "release_artist_name": "Izïa",
                "release_artist_names": [
                    "Izïa"
                ],
                "release_msid": "5f1c810a-8f53-429d-b068-8920a77f8093",
                "tracknumber": 1
            },
            "artist_name": "Izïa",
            "release_name": "Trop vite",
            "track_name": "Trop vite - Version single"
        }
    },
    {
        "track_metadata": {
            "additional_info": {
                "artist_msid": "c69f68ca-d380-43bb-b32f-376b8ece7b87",
                "rating": "",
                "recording_mbid": "",
                "release_msid": "f987398c-9f49-4aaa-b86d-1d394be09318",
                "source": "P",
                "track_length": "241",
                "track_number": "3/20"
            },
            "artist_name": "Nina Nikolina",
            "release_name": "",
            "track_name": "Pusta Hubost"
        }
    }
]

@api_bp.route("/odyssey/<mbid0>/<mbid1>")
@crossdomain(headers="Authorization, Content-Type")
@ratelimit()
def odyssey(mbid0, mbid1):
 
    steps = _parse_int_arg("steps")

    return jsonify({'status': 'ok', 'payload': fakeData})


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
