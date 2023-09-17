#!/usr/bin/env python3
from pprint import pprint
from erl_comm.http_client import (
    ConnInfo,
    send_ping,
    send_start_ep,
    send_stop_ep,
    send_start_phase,
    send_stop_phase,
    send_info,
)


def main():
    conn_info = ConnInfo(
        url="https://ecs-mnemosyne.azurewebsites.net/api/Hub",
        robot_id="f6e43a38-2222-4c2f-e61b-08dbb36c5a96",
        competition_id="ERL",
    )
    try:
        print(f"ping: {send_ping(conn_info=conn_info)}")
        print(f"start episode 4: {send_start_ep(conn_info, 4)}")
        print(f"start ep 4, phase 1: {send_start_phase(conn_info, 4, 1)}")
        resp = send_info(conn_info, 4, 1, "Hello world")
        print(f"info for ep 4, phase 1: {resp}")
        print(f"stop ep 4, phase 1: {send_stop_phase(conn_info, 4, 1)}")
        print(f"stop ep 4: {send_stop_ep(conn_info, 4)}")
    except Exception as e:
        print(f"caught '{type(e)}'")
        pprint(e)


if __name__ == "__main__":
    main()
