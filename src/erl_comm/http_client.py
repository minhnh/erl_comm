"""
Module containing HTTP requests according to the ERL Robot API Guide Version 1.0.1a.
"""
from enum import StrEnum
import requests


class ActionType(StrEnum):
    PING = "PING"  # Informs the Hub the Robot is active
    EPISODES = "EPISODES"  # Returns a list of Episode and Phase numbers and name
    ITEMS = "ITEMS"  # Returns a list of Items for a specific Episode and Phase
    START_EP = "STARTEPISODE"  # Informs the Hub the Robot has started an Episode
    STOP_EP = "STOPEPISODE"  # Informs the Hub the Robot has stopped/completed an Episode
    START_PHASE = "STARTPHASE"  # Informs the Hub the Robot has started a Phase
    STOP_PHASE = "STOPPHASE"  # Informs the Hub the Robot has stopped a Phase
    INFO = "INFO"  # A general message from the Robot


class RequestKey(StrEnum):
    ROBOT_ID = "RobotId"
    COMP = "Competition"
    ACTION = "Action"
    EPISODE = "Episode"
    PHASE = "Phase"
    MSG = "Message"


class RespKey(StrEnum):
    SUCCESS = "success"
    MSG = "message"
    ITEMS = "items"
    EPISODES = "episodes"
    PHASES = "phases"
    NAME = "name"
    NUM = "number"
    CODE = "code"
    LOC = "location"


class ConnInfo(object):
    def __init__(self, url: str, robot_id: str, competition_id: str) -> None:
        self.url = url
        self.robot_id = robot_id
        self.competition_id = competition_id


class ItemInfo(object):
    def __init__(self, code: str, name: str, location: str) -> None:
        self.code = code
        self.name = name
        self.location = location

    def __str__(self):
        return f"{self.name} ({self.code})"


class PhaseInfo(object):
    def __init__(self, ep_num: int, num: int, name: str) -> None:
        self.episode_number = ep_num
        self.number = num
        self.name = name

    def __str__(self):
        return f"ep {self.episode_number}, phase {self.number}: {self.name}"


class EpisodeInfo(object):
    def __init__(self, num: int, name: str) -> None:
        self.number = num
        self.name = name
        self.phases = {}  # dictionary mapping phase number to PhaseInfo

    def __str__(self):
        return f"episode {self.number}: {self.name} ({len(self.phases)} phases)"

    def add_phase(self, phase: PhaseInfo) -> None:
        if phase.number in self.phases:
            raise RuntimeError(f"phase '{phase.number} ({phase.name})' already added to episode")
        self.phases[phase.number] = phase


def get_default_json(conn_info: ConnInfo) -> dict:
    return {
        RequestKey.ROBOT_ID: conn_info.robot_id,
        RequestKey.COMP: conn_info.competition_id,
    }


def get_action_json(conn_info: ConnInfo, action: ActionType) -> dict:
    json_req = get_default_json(conn_info)
    json_req[RequestKey.ACTION] = action
    return json_req


def send_http_req(url: str, json_data: dict) -> dict:
    resp = requests.post(url, json=json_data).json()
    if RespKey.SUCCESS in resp:
        return resp

    if "status" in resp:
        status = resp["status"]
        if "title" in resp:
            err_msg = resp["title"]
        else:
            err_msg = "<empty>"
        raise RuntimeError(f"unexpected response: status={status}, msg={err_msg}")

    raise RuntimeError(f"unexpected response: {resp}")


def send_ping(conn_info: ConnInfo) -> bool:
    resp = send_http_req(conn_info.url, json_data=get_action_json(conn_info, ActionType.PING))
    return resp[RespKey.SUCCESS]


def send_start_ep(conn_info: ConnInfo, ep_num: int) -> bool:
    json_data = get_action_json(conn_info, ActionType.START_EP)
    json_data[RequestKey.EPISODE] = ep_num
    resp = send_http_req(conn_info.url, json_data=json_data)
    return resp[RespKey.SUCCESS]


def send_stop_ep(conn_info: ConnInfo, ep_num: int) -> bool:
    json_data = get_action_json(conn_info, ActionType.STOP_EP)
    json_data[RequestKey.EPISODE] = ep_num
    resp = send_http_req(conn_info.url, json_data=json_data)
    return resp[RespKey.SUCCESS]


def send_start_phase(conn_info: ConnInfo, ep_num: int, phase_num: int) -> bool:
    json_data = get_action_json(conn_info, ActionType.START_PHASE)
    json_data[RequestKey.EPISODE] = ep_num
    json_data[RequestKey.PHASE] = phase_num
    resp = send_http_req(conn_info.url, json_data=json_data)
    return resp[RespKey.SUCCESS]


def send_stop_phase(conn_info: ConnInfo, ep_num: int, phase_num: int) -> bool:
    json_data = get_action_json(conn_info, ActionType.STOP_PHASE)
    json_data[RequestKey.EPISODE] = ep_num
    json_data[RequestKey.PHASE] = phase_num
    resp = send_http_req(conn_info.url, json_data=json_data)
    return resp[RespKey.SUCCESS]


def send_info(conn_info: ConnInfo, ep_num: int, phase_num: int, msg: str) -> bool:
    json_data = get_action_json(conn_info, ActionType.INFO)
    json_data[RequestKey.EPISODE] = ep_num
    json_data[RequestKey.PHASE] = phase_num
    json_data[RequestKey.MSG] = msg
    resp = send_http_req(conn_info.url, json_data=json_data)
    return resp[RespKey.SUCCESS]


def get_episodes(conn_info: ConnInfo) -> list:
    json_data = get_action_json(conn_info, ActionType.EPISODES)
    resp = send_http_req(conn_info.url, json_data=json_data)
    if resp[RespKey.SUCCESS]:
        return resp[RespKey.EPISODES]
    if RespKey.MSG in resp:
        err_msg = f" ({resp[RespKey.MSG]})"
    else:
        err_msg = ""
    raise RuntimeError(f"failed to query for episodes{err_msg}")


def process_episodes_data(episodes_data: list) -> dict:
    """Returns dictionary of EpisodeInfo objects.

    Convert a list of episodes json data into EpisodeInfo objects containing info about
    episodes and phases. Return a dictionary mapping episode number to a corresponding
    EpisodeInfo object
    """
    episodes = {}
    for ep_data in episodes_data:
        assert RespKey.NUM in ep_data, f"episode data missing required key '{RespKey.NUM}'"
        assert RespKey.NAME in ep_data, f"episode data missing required key '{RespKey.NAME}'"
        assert RespKey.PHASES in ep_data, f"episode data missing required key '{RespKey.PHASES}'"

        ep_num = ep_data[RespKey.NUM]
        ep_name = ep_data[RespKey.NAME]
        ep_info = EpisodeInfo(ep_num, ep_name)
        for phase_data in ep_data[RespKey.PHASES]:
            assert RespKey.NUM in phase_data, f"phase data missing required key '{RespKey.NUM}'"
            assert RespKey.NAME in phase_data, f"phase data missing required key '{RespKey.NAME}'"
            phase_info = PhaseInfo(ep_num, phase_data[RespKey.NUM], phase_data[RespKey.NAME])
            ep_info.add_phase(phase_info)

        episodes[ep_num] = ep_info

    return episodes


def get_items(conn_info: ConnInfo, ep_num: int, phase_num: int) -> list:
    json_data = get_action_json(conn_info, ActionType.ITEMS)
    json_data[RequestKey.EPISODE] = ep_num
    json_data[RequestKey.PHASE] = phase_num
    resp = send_http_req(conn_info.url, json_data=json_data)
    if resp[RespKey.SUCCESS]:
        return resp[RespKey.ITEMS]
    return []


def process_items_data(items_data: list) -> dict:
    """Returns dictionary of ItemInfo objects.

    Convert a list of items json data into ItemInfo objects containing info about
    items in each phase.
    """
    items_info = {}
    for it_data in items_data:
        assert RespKey.CODE in it_data, f"item data missing required key '{RespKey.CODE}'"
        assert RespKey.NAME in it_data, f"item data missing required key '{RespKey.NAME}'"
        assert RespKey.LOC in it_data, f"item data missing required key '{RespKey.LOC}'"

        it_info = ItemInfo(it_data[RespKey.CODE], it_data[RespKey.NAME], it_data[RespKey.LOC])
        if it_info.code in items_info:
            raise RuntimeError(f"duplicate item: {it_info.code}")
        items_info[it_info.code] = it_info

    return items_info
