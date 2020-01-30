"""
Classify loops through all the ads and save the scores to the database.
"""
import click
import dill
from classifier.utilities import (confs, DB)
import json
import spacy

# DATABASE_URL="postgres:///facebook_ads" pipenv run ./classify parse_waist_json --every


AGE_OFFSET = 12 # Facebook seems to reflect ages as the age in years minus twelve. So, 65 is reflected in JSON as 53. Weird.

GENDER_CROSSWALK = {
    "MALE": "men",
    "FEMALE": "women"
}


@click.command("parse_waist_json")
# @click.option("--newest/--every",
#               default=True,
#               help="Classify all of the records")
@click.pass_context
def parse_waist_json(ctx):
    """
    Classify the ads in the database at $DATABASE_URL.
    """

    # takes 8s locally
    query = "select * from fbpac_ads where targets = '[]' and targeting is not null and targeting ilike '{%'"

    total = "select count(*) as length from ({}) as t1;"
    length = DB.query(total.format(query))[0]["length"]
    records = DB.query(query)
    print("found {} ads".format(length))
    updates = []
    query = "update fbpac_ads set targets=:targets where id=:id"
    idx = 0
    for record in records:
        idx += 1
        record_lang = "en-US" if record["lang"] == "en-IE" else record["lang"]
        
        advertiser = record["advertiser"]

        created_at = record["created_at"]

        data = json.loads(record["targeting"])
        if record["targeting"][0] == '{' and "waist_targeting_data" in data:
            targeting = data["waist_targeting_data"] # this is necessary for all post Nov 13 - Dec 6 data.
        elif record["targeting"][0] == '{' and "data" in data:
            targeting = data["data"]["waist_targeting_data"] # this is necessary for all post Jan 29 (ATI code) data
        else:
            targeting = data
        if not advertiser and "waist_advertiser_info" in data:
            advertiser = data["waist_advertiser_info"]["name"]

        targets = parse_one_waist_json(targeting)

        # TODO: it appears there are never multiple distinct JSONs for one ad (besides diff profile_picture_url query strings and diff date formats)
        # look at Thanos's code from FB listing all the possibilities

        update = {
            "id": record["id"],
            "targets": json.dumps(targets)
        }
        updates.append(update)
        out = "Parsed {pid[id]} ({info[idx]} of {info[length]}) with {pid[targets]}"
        print(out.format(pid=update, info={"length": length, "idx": idx}))

        if len(updates) >= 100 and True:
            DB.bulk_query(query, updates)
            updates = []

    if updates and True:
        DB.bulk_query(query, updates)


def parse_one_waist_json(targeting):
    targets = []
    for elem in targeting:
        if elem["__typename"] == "WAISTUICustomAudienceType":
            if elem["waist_ui_type"] == "CUSTOM_AUDIENCES_WEBSITE":
                targets += [["Website", "people who have visited their website or used one of their apps"]]
            elif elem["waist_ui_type"] == "CUSTOM_AUDIENCES_ENGAGEMENT_PAGE":
                targets += [["Activity on the Facebook Family", "fb page"]] # https://www.facebook.com/business/help/221146184973131?id=2469097953376494
            elif elem["waist_ui_type"] == "CUSTOM_AUDIENCES_ENGAGEMENT_IG":
                targets += [["Activity on the Facebook Family", "instagram"]] # https://www.facebook.com/business/help/221146184973131?id=2469097953376494
            elif elem["waist_ui_type"] == "CUSTOM_AUDIENCES_LOOKALIKE":
                targets += [["Retargeting", "people who may be similar to their customers"]]
            elif elem["waist_ui_type"] == "CUSTOM_AUDIENCES_DATAFILE":  # new to Python
                targets += [["List", ""]]
            elif elem["waist_ui_type"] == "CUSTOM_AUDIENCES_ENGAGEMENT_VIDEO":  # new to Python
                targets += [["Activity on the Facebook Family", "video"]] # https://www.facebook.com/business/help/221146184973131?id=2469097953376494
            else:
                print("UNKNOWN waist UI type: {}".format(elem["waist_ui_type"]))
                # haven't seen these yet.
                # CUSTOM_AUDIENCES_OFFLINE
                # CUSTOM_AUDIENCES_MOBILE_APP
                # CUSTOM_AUDIENCES_ENGAGEMENT_LEAD_GEN
                # CUSTOM_AUDIENCES_ENGAGEMENT_CANVAS
                # CUSTOM_AUDIENCES_ENGAGEMENT_EVENT
                # CUSTOM_AUDIENCES_UNRESOLVED
                # CUSTOM_AUDIENCES_STORE_VISITS


        elif elem["__typename"] ==  "WAISTUIAgeGenderType":
            # {"__typename"=>"WAISTUIAgeGenderType", "waist_ui_type"=>"AGE_GENDER", "age_min"=>23, "age_max"=>53, "gender"=>"ANY",  "id"=>"V0FJU1RVSUFnZUdlbmRlclR5cGU6MjM1Mw==", "serialized_data"=>"{\"age_min\":23,\"age_max\":53,\"gender\":null}",}
            targets += [
                ["MinAge", elem["age_min"] + AGE_OFFSET], 
                ["MaxAge", elem["age_max"] + AGE_OFFSET] if elem["age_max"] != 53 else None, 
                ["Age", ("{} and older".format(elem["age_min"] + AGE_OFFSET) if elem["age_max"] == 53 else ("{} and younger".format(elem["age_max"] + AGE_OFFSET) if elem["age_min"] == 0  else "{} to {}".format(elem["age_min"] + AGE_OFFSET, elem["age_max"] + AGE_OFFSET)))], # TODO. 30 to 45, 45 and older,  35 and younger
                ["Gender", GENDER_CROSSWALK[elem["gender"]]] if elem["gender"] != "ANY" else None
            ]
        elif elem["__typename"] ==  "WAISTUILocationType":
            # {"__typename"=>"WAISTUILocationType", "id"=>"V0FJU1RVSUxvY2F0aW9uVHlwZTpjaXR5LmhvbWUuMjQzMDUzNg==", "serialized_data"=>"{\"location_granularity\":\"city\",\"location_geo_type\":\"home\",\"location_code\":\"2430536\"}", "waist_ui_type"=>"LOCATION", "location_name"=>"Atlanta, Georgia", "location_type"=>"HOME"}
            # {"__typename"=>"WAISTUILocationType", "id"=>"V0FJU1RVSUxvY2F0aW9uVHlwZTpjb3VudHJ5LmhvbWUuVVM=", "serialized_data"=>"{\"location_granularity\":\"country\",\"location_geo_type\":\"home\",\"location_code\":\"US\"}", "waist_ui_type"=>"LOCATION", "location_name"=>"the United States", "location_type"=>"HOME"}
            # City... Occasionally has a comma in it. 
            # State # only in city state pairs
            # Region # e.g. United States, California
            granularity = json.loads(elem["serialized_data"])["location_granularity"] 
            if granularity == "city":
                *city, state = elem["location_name"].split(",")
                locs = [["City", city], ["State", state]]
            elif granularity == "region":
                locs = [["Region", elem["location_name"]]]
            elif granularity == "country":
                locs = [["Country", elem["location_name"]]]
            else:
                print("UNKNOWN location_granularity: {}".format(json.loads(elem["serialized_data"])["location_granularity"] ))
                locs = [[]]
            targets += locs + [["Location Granularity", json.loads(elem["serialized_data"])["location_granularity"] ], ["Location Type", elem["location_type"]]]
        elif elem["__typename"] ==  "WAISTUILocaleType":
            targets += [["Language", l] for l in elem["locales"]]
        elif elem["__typename"] ==  "WAISTUIInterestsType":
            targets += [["Interest", i["name"]] for i in elem["interests"]]
        elif elem["__typename"] ==  "WAISTUIBCTType": # thus far, likely engagement with conservative content
            targets += [["Segment", elem["name"]]]
        elif elem["__typename"] ==  "WAISTUIEduStatusType":
            targets += [["Education", elem["edu_status"]], ["Segment", "Bachelor's degree" if elem["edu_status"] == "EDU_COLLEGE_ALUMNUS" else elem["edu_status"] ]]
        elif elem["__typename"] ==  "WAISTUIConnectionType": # new to Python
            targets += [["Like", "Likes Page"]]
        elif elem["__typename"] ==  "WAISTUIEduSchoolsType": # new to Python
        # {'__typename': 'WAISTUIEduSchoolsType', 'id': 'V0FJU1RVSUVkdVNjaG9vbHNUeXBlOjg3ODczNjkzMTQx', 'serialized_data': '{"school_ids":[87873693141]}', 'waist_ui_type': 'EDU_SCHOOLS', 'school_names': ['Boston College']}
            targets += [["Education", school] for school in elem["school_names"]]
        elif elem["__typename"] ==  "WAISTUIFriendsOfConnectionType": # new to Python
            # print(elem)
            targets += [["Like", "Friend Likes Page"]]
            pass
        elif elem["__typename"] ==  "WAISTUIWorkEmployerType":
            targets += ["Education", elem["employer_name"]]
        else:
            print("Unknown WAIST type {}".format(elem["__typename"]))

            # no examples of these yet
            # WAISTUIActionableInsightsType
            # WAISTUIBrandedContentWithPageType
            # WAISTUICollaborativeAdType
            # WAISTUIDPAType
            # WAISTUIRelationshipType
            # WAISTUIJobTitleType

    return [t for t in targets if t]
