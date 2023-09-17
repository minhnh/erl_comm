from enum import StrEnum
import requests


class ActionType(StrEnum):
    PING = "PING"  # Informs the Hub the Robot is active
    EPISODES = "EPISODES"  # Returns a list of Episode and Phase numbers and names that
    # must be provided when requesting other data from the Hub.
    ITEMS = "ITEMS"  # Returns a list of Items for a specific Episode and Phase.
    STARTEPISODE = "STARTEPISODE"  # Informs the Hub the Robot has started an Episode.
    STOPEPISODE = "STOPEPISODE"  # Informs the Hub the Robot has stopped/completed an Episode.
    STARTPHASE = "STARTPHASE"  # Informs the Hub the Robot has started a Phase.
    STOPPHASE = "STOPPHASE"  # Informs the Hub the Robot has stopped a Phase.
    INFO = "INFO"  # A general message from the Robot.


class RequestKey(StrEnum):
    ROBOT_ID = "RobotId"
    COMP = "Competition"
    ACTION = "Action"
    EPISODE = "Episode"
    PHASE = "Phase"


class RespKey(StrEnum):
    SUCCESS = "success"
    MSG = "message"
    ITEMS = "items"
    EPISODES = "episodes"


class ConnInfo(object):
    def __init__(self, url: str, robot_id: str, competition_id: str):
        self.url = url
        self.robot_id = robot_id
        self.competition_id = competition_id


def get_default_json(conn_info: ConnInfo) -> dict:
    return {
        RequestKey.ROBOT_ID: conn_info.robot_id,
        RequestKey.COMP: conn_info.competition_id,
    }


def get_ping_json(conn_info: ConnInfo) -> dict:
    json_req = get_default_json(conn_info)
    json_req[RequestKey.ACTION] = ActionType.PING
    return json_req


def send_http_req(url: str, json_data: dict) -> dict:
    resp_json = requests.post(url, json=json_data).json()
    if RespKey.SUCCESS in resp_json:
        return resp_json

    if "status" in resp_json:
        status = resp_json["status"]
        if "title" in resp_json:
            err_msg = resp_json["title"]
        else:
            err_msg = "<empty>"
        raise RuntimeError(f"unexpected response: status={status}, msg={err_msg}")

    raise RuntimeError(f"unexpected response: {resp_json}")


def send_ping(conn_info: ConnInfo) -> bool:
    resp_json = send_http_req(conn_info.url, json_data=get_ping_json(conn_info))
    return resp_json[RespKey.SUCCESS]
