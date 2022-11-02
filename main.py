import argparse
from typing import Optional
import typer
import requests
import json
from datetime import datetime

app = typer.Typer()

URL = "https://rickandmortyapi.com/api/"
COMMANDS = {0: "character/", 1: "location/", 2: "episode/"}


def get_request(request: str):
    """
    get request
    :param request: the type of thing(ch,loc,ep)
    :return: the response
    """
    x = requests.get(URL + request).json()
    if "results" in x.keys():
        all_pages = x["results"]
        while x["info"]["next"]:
            x = requests.get(x["info"]["next"]).json()
            all_pages += x["results"]
    else:
        all_pages = x["error"]
    return all_pages


def get_id(request: str):
    """
    get request by id
    :param request: the type of thing(ch,loc,ep)
    :return: the response
    """
    x = requests.get(URL + request).json()
    return x


@app.command()
def ls(characters: Optional[bool] = typer.Option(False, "--characters", "-c"),
       locations: Optional[bool] = typer.Option(False, "--locations", "-l"),
       episodes: Optional[bool] = typer.Option(False, "--episodes", "-e"),
       ):
    """
    shows everything acording to filters
    :param characters: shows characters
    :param locations: shows location
    :param episodes: shows episode
    :return: everything according to filters
    """
    lst = locals()
    output = []
    if_no_arg = True
    num_of_command = 0
    for i in lst:
        if lst[i]:
            if_no_arg = False
            output += get_request(COMMANDS[num_of_command])
        num_of_command += 1
    if if_no_arg:
        for i in range(len(lst)):
            output += get_request(COMMANDS[i])
    print(json.dumps(output, indent=4))


def filter_request(args, type_filter: int):
    """

    :param args: arguments/filtes
    :param type_filter: character/episodes/location
    :return: repsonse according to filters
    """
    filter_args = '?'
    for key in args:
        if not args[key] == "":
            filter_args += str(key) + "=" + str(args[key]) + "&"
    response = get_request(COMMANDS[type_filter] + filter_args)
    return response


def spec_ch_og_filter(results, input):
    """
    filters character according to origin
    :param results: all the characters
    :param input: origin
    :return: response
    """
    final_response = []
    for key in results:
        if key["origin"]["name"] == input:
            final_response.append(key)
    return final_response


def spec_ch_loc_filter(results, input):
    """
        filters character according to location
        :param results: all the characters
        :param input: location
        :return: response
        """
    final_response = []
    for key in results:
        if key["location"]["name"] == input:
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
        id: Optional[int] = typer.Option("", "--id", "-i")
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
    """
    args = locals()
    response = filter_request(args, 0)
    if location != "":
        response = spec_ch_loc_filter(response, location)
    if origin != "":
        response = spec_ch_og_filter(response, origin)
    if id is not None:
        response = get_id(COMMANDS[0] + str(id))
    print(json.dumps(response, indent=4))


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
    """
    args = locals()
    response = filter_request(args, 1)
    if id is not None:
        response = get_id(COMMANDS[1] + str(id))
    print(json.dumps(response, indent=4))


def date_comp(input, key, is_after):
    """
    comparing dates
    :param input: date of input
    :param key: date of episode
    :param is_after: boolean if after
    :return: true if is_After and comparison is true
    """
    d1 = datetime.strptime(input, '%B %d, %Y').date()
    d2 = datetime.strptime(key["air_date"], '%B %d, %Y').date()
    if is_after:
        return d2 > d1
    else:
        return d2 < d1


def spec_ep_ep_filter(results, input):
    """
    specific filter - for episodes according to episode num
    :param results: list of episodes
    :param input: the episode num
    :return: the response
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
    """
    args = locals()
    response = filter_request(args, 2)
    if before != "":
        response = spec_ep_aft_bef_filter(response, before, False)
    if after != "":
        response = spec_ep_aft_bef_filter(response, after, True)
    if season is not None:
        response = spec_ep_sea_filter(response, season)
    if episode_num is not None:
        response = spec_ep_ep_filter(response, episode_num)
    if id is not None:
        response = get_id(COMMANDS[2] + str(id))
    print(json.dumps(response, indent=4))


@app.command()
def metrics(
        limit: Optional[int] = typer.Option(None, "--limit", "-l")
):
    """
    prints the metrics
    :param limit: optional limit for the metric list
    :return: prints the characters and metrics
    """
    results = get_request(COMMANDS[0])
    character_counter = {}

    for result in results:
        character_counter[result["id"]] = len(result["episode"])
    if limit is None:
        sorted_characters = dict(sorted(character_counter.items(), key=lambda item: item[1], reverse=True))
    else:
        sorted_characters = dict(sorted(character_counter.items(), key=lambda item: item[1], reverse=True)[:limit])
    for i in sorted_characters:
        print((get_id(COMMANDS[0] + str(i))["name"]) + "  " + str(character_counter[i]))



if __name__ == "__main__":
    app()
