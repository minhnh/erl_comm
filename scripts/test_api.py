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
    get_episodes,
    process_episodes_data,
    get_items,
    process_items_data,
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
        episodes_data = get_episodes(conn_info)
        items_data = get_items(conn_info, 4, 1)
        print(f"stop ep 4, phase 1: {send_stop_phase(conn_info, 4, 1)}")
        print(f"stop ep 4: {send_stop_ep(conn_info, 4)}")
    except Exception as e:
        print(f"caught '{type(e)}'")
        pprint(e)

    processed_eps = process_episodes_data(episodes_data)
    for _, ep_info in processed_eps.items():
        print(ep_info)
        for _, phase_info in ep_info.phases.items():
            print(f"  {phase_info}")

    processed_items = process_items_data(items_data)
    print("found the following items:")
    for _, item_info in processed_items.items():
        print("  ", item_info)


if __name__ == "__main__":
    main()
