#!/usr/bin/env python
import argparse
from datetime import datetime
from riot import REGIONS, RiotAPI, MatchData

def parse_args(inputs=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--name", help="Summoner name", required=False, default="ioki")
    parser.add_argument("--region", choices=REGIONS, help="LoL regions", required=False, default="na1")
    parser.add_argument("--depth", required=False, help="Search queue gepth", default=20)
    parser.add_argument("--no-wait", required=False, action="store_true",
                        help="Terminate script, when API Key limit is reached")

    return vars(parser.parse_args())

def get_compresed_history(riot: RiotAPI, name: str, since: int = None) -> str:
    loses = [
        stringify(riot.get_match_data(match_id).is_winner(name))
        for match_id in riot.get_matches(name, since=since)
    ]
    return " ".join(loses)

def pnd(riot: RiotAPI, name: str, since: int = None) -> bool:
    for match_id in riot.get_matches(name, since=since):
        match = riot.get_match_data(match_id)
        yield stringify(match.is_winner(name))

def stringify(result: bool) -> str:
    return "_" if result else "X"


def main(api_key):
    args = parse_args()
    name = args["name"]
    print(args)
    rito = RiotAPI(region=args["region"], api_key=api_key, q_depth=args["depth"],
                   wait_on_limit=not args["no_wait"])
    print(f"Name: {name}")
    # print(get_compresed_history(rito, name))
    for match_id in rito.get_matches(name):
        match_data = rito.get_match_data(match_id)
        print(f"Match: {match_id} -> {stringify(match_data.is_winner(name))}", end='')
        time = datetime.utcfromtimestamp(int(match_data.get_timestamp()/1000))
        print(f" <- at {time} ({match_data.get_timestamp()})")
        print(f"Teammates:")
        for mate_acc_id in match_data.get_team_members_acc_ids(name):
            mate = match_data.get_account_name(mate_acc_id)
            print(f"{mate:>20}: ", end="", flush=True)
            # NOTE: first try to find matches by name
            # if it doesn't work try acc_id
            # (weirdly enough acc_ids doesn't match very often,
            #  perhaps the account shit in the begging of the season?)
            # NOTE: we don't use 'get_compresed_history' 
            # unrolling the function provides better responce on cmd 
            # (no need to wait for full Q to populate) 
            sub_match_ids = rito.get_matches(mate, since=match_data.get_timestamp())
            if sub_match_ids is None:
                sub_match_ids = rito.get_matches_by_acc_id(mate_acc_id, since=match_data.get_timestamp())

            for sub_match_id in sub_match_ids:
                sub_match_data = rito.get_match_data(sub_match_id)
                print(f"{stringify(sub_match_data.is_winner(mate))} ", end='', flush=True)
            print()
            # print(get_compresed_history(rito, mate, match_data.get_timestamp()))
        print()


def pnd(api_key):
    rito = RiotAPI('na1', api_key)
    rito.get_matches('ioki')
    rito.get_match_data(3292997059)


if __name__ == "__main__":
    try:
        api_key = open(".api_key").read()
    except IOError:
        print("Somiething is not right with your '.api_key' file")
        exit(-1)

    exit(main(api_key))
    # exit(pnd(api_key))