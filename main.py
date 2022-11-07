from typing import Optional
import typer
import requests
import json
from datetime import datetime
import pandas as pd
import numpy as np


app = typer.Typer()

URL = "https://rickandmortyapi.com/api/"
COMMANDS = {"CHARACTER": "character/", "LOCATION": "location/", "EPISODE": "episode/"}
IS_TABLE = False


def get_request_all_pages(request: str):
    """
    get request
    :param request: the type of thing(ch,loc,ep)
    :return: the response
    :rtype: list
    """
    response = requests.get(URL + request).json()
    all_pages = response
    if "results" in response.keys():
        all_pages = response["results"]
        while response["info"]["next"]:
            response = requests.get(response["info"]["next"]).json()
            all_pages += response["results"]
    elif "error" is response.keys():
        all_pages = response["error"]
    return all_pages


@app.command()
def show(characters: Optional[bool] = typer.Option(False, "--characters", "-c"),
         locations: Optional[bool] = typer.Option(False, "--locations", "-l"),
         episodes: Optional[bool] = typer.Option(False, "--episodes", "-e"),
         ):
    """
    shows everything acording to filters
    :param characters: shows characters
    :param locations: shows location
    :param episodes: shows episode
    :return: prints everything according to filters
    :rtype: None
    """
    lst = [characters, locations, episodes]
    output = []
    if_no_arg = True
    for count, key in enumerate(COMMANDS):
        if lst[count]:
            if_no_arg = False
            output += get_request_all_pages(COMMANDS[key])
    if if_no_arg:
        for count, key in enumerate(COMMANDS):
            output += get_request_all_pages(COMMANDS[key])
    print_results(output)

def filter_request(args, type_filter: str):
    """

    :param args: arguments/filtes
    :param type_filter: character/episodes/location
    :return: repsonse according to filters
    :rtype: list
    """
    filter_args = '?'
    for key in args:
        if not args[key] == "":
            filter_args += str(key) + "=" + str(args[key]) + "&"
    response = get_request_all_pages(COMMANDS[type_filter] + filter_args)
    return response


def spec_ch_og_filter(results, input, filter):
    """
    filters character according to origin
    :param results: all the characters
    :param input: origin
    :return: response
    :rtype: None
    """
    final_response = []
    for key in results:
        if key[filter]["name"] == input:
            final_response.append(key)
    return final_response


@app.command()
def character(
        name: Optional[str] = typer.Option("", "--name", "-n"),
        status: Optional[str] = typer.Option("", "--status"),
        species: Optional[str] = typer.Option("", "--species"),
        type: Optional[str] = typer.Option("", "--type", "-t"),
        gender: Optional[str] = typer.Option("", "--gender", "-g"),
        location: Optional[str] = typer.Option("", "--location", "-l"),
        origin: Optional[str] = typer.Option("", "--origin", "-o"),
        id: Optional[int] = typer.Option(None, "--id", "-i")
):
    """
    returns all the characters according to filters
    :param name: name of character
    :param status: status of character
    :param species: species of character
    :param type: type of character
    :param gender: gender of character
    :param location: location of character
    :param origin: origin of character
    :param id: id of character
    :return: returns all the characters according to filters
    :rtype: None
    """
    args = locals()
    response = filter_request(args, "CHARACTER")
    if location != "":
        response = spec_ch_og_filter(response, location, "location")
    if origin != "":
        response = spec_ch_og_filter(response, origin, "origin")
    if id is not None:
        response = get_request_all_pages(COMMANDS["CHARACTER"] + str(id))
    print_results(response)

@app.command()
def location(
        name: Optional[str] = typer.Option("", "--name", "-n"),
        id: Optional[int] = typer.Option(None, "--id", "-i"),
        type: Optional[str] = typer.Option("", "--type", "-t"),
        dimension: Optional[str] = typer.Option("", "--dimension", "-d")
):
    """
    returns location according to filters
    :param name: name of location
    :param id: id of location
    :param type: type of locatin
    :param dimension: dimension of location
    :return: returns location according to filters
    :rtype: None
    """
    args = locals()
    response = filter_request(args, "LOCATION")
    if id is not None:
        response = get_request_all_pages(COMMANDS["LOCATION"] + str(id))
    print_results(response)


def date_comp(input, key, is_after):
    """
    comparing dates
    :param input: date of input
    :param key: date of episode
    :param is_after: boolean if after
    :return: true if is_After and comparison is true
    :rtype: bool
    """
    d2 = datetime.strptime(key["air_date"], '%B %d, %Y').date()
    try:
        d1 = datetime.strptime(input, '%B %d, %Y').date()
        if is_after:
            return d2 > d1
        else:
            return d2 < d1
    except:
        print("use the format '<Month> <number>, <year>'")
        exit(1)


def spec_ep_ep_filter(results, input):
    """
    specific filter - for episodes according to episode num
    :param results: list of episodes
    :param input: the episode num
    :return: the response
    :rtype: list
    """
    final_response = []
    for key in results:
        code = key["episode"]
        if int(code[code.index("E") + 1:]) == int(input):
            final_response.append(key)
    return final_response


def spec_ep_sea_filter(results, input):
    """
    specific filter - for episodes according to season
    :param results: list of episodes
    :param input: the season
    :return: the response
    :rtype: str
    """
    final_response = []
    for key in results:
        code = key["episode"]
        if int(code[code.index("S") + 1:code.index("E")]) == int(input):
            final_response.append(key)
    return final_response


def spec_ep_aft_bef_filter(results, input, is_after):
    """
    gets the episodes before or after a specific date in format "Month num, year"
    :param results: list of episodes
    :param input: the date
    :param is_after: if its after or before
    :return: the response
    :rtype: list
    """
    final_response = []
    for key in results:
        if date_comp(input, key, is_after):
            final_response.append(key)
    return final_response


@app.command()
def episode(
        name: Optional[str] = typer.Option("", "--name", "-n"),
        id: Optional[int] = typer.Option(None, "--id", "-i"),
        episode: Optional[str] = typer.Option("", "--episode", "-e"),
        before: Optional[str] = typer.Option("", "--before", "-b"),
        after: Optional[str] = typer.Option("", "--after", "-a"),
        season: Optional[int] = typer.Option(None, "--season", "-s"),
        episode_num: Optional[int] = typer.Option(None, "--episode-num")
):
    """
    prints all episodes acording to filters
    :param name: name of episode
    :param id: id of episode
    :param episode: code of episode
    :param before: date and prints everything before
    :param after: date and prints everything after
    :param season: prints all episodes of season
    :param episode_num: prints all epidosde of episode
    :return: prints all episodes acording to filters
    :rtype: list
    """
    args = locals()
    response = filter_request(args, "EPISODE")
    if before != "":
        response = spec_ep_aft_bef_filter(response, before, False)
    if after != "":
        response = spec_ep_aft_bef_filter(response, after, True)
    if season is not None:
        response = spec_ep_sea_filter(response, season)
    if episode_num is not None:
        response = spec_ep_ep_filter(response, episode_num)
    if id is not None:
        response = get_request_all_pages(COMMANDS["EPISODE"] + str(id))
    print_results(response)


@app.command()
def metrics(
        limit: Optional[int] = typer.Option(None, "--limit", "-l")
):
    """
    prints the metrics
    :param limit: optional limit for the metric list
    :return: prints the characters and metrics
    :rtype: None
    """
    results = get_request_all_pages(COMMANDS[0])
    character_counter = {}
    for result in results:
        character_counter[result["id"]] = len(result["episode"])
    if limit is None:
        sorted_characters = dict(sorted(character_counter.items(), key=lambda item: item[1], reverse=True))
    else:
        sorted_characters = dict(sorted(character_counter.items(), key=lambda item: item[1], reverse=True)[:limit])
    for i in sorted_characters:
        print((get_request_all_pages(COMMANDS["CHARACTER"] + str(i))["name"]) + "  " + str(character_counter[i]))


def print_results(results):
    """
    prints results either as a table or as json documents
    """
    if IS_TABLE:
        df = pd.DataFrame(results)
        print(df)
    else:
        print(json.dumps(results, indent=4))


@app.callback()
def main(table: bool = False):
    """
    checks if user wants it as a tbale or json
    """
    global IS_TABLE
    IS_TABLE = table


if __name__ == "__main__":
    app()
