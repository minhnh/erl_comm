#!/usr/bin/env python3
from pprint import pprint
from erl_comm.http_client import ConnInfo, send_ping


def main():
    conn_info = ConnInfo(
        url="https://ecs-mnemosyne.azurewebsites.net/api/Hub",
        robot_id="f6e43a38-2222-4c2f-e61b-08dbb36c5a96",
        competition_id="ERL",
    )
    pprint(send_ping(conn_info=conn_info))


if __name__ == "__main__":
    main()
