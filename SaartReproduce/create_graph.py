from SaartReproduce.classes import *
import json
from typing import Dict


def load_from_disk(path) -> Dict[str, Node]:
    channels_json = json.load(open(path, 'rb'))
    nodes = {}
    # lnd format
    for channel in channels_json['edges']:
        if not channel["node1_policy"] and not channel["node2_policy"]:
            continue
        if channel['node1_pub'] not in nodes: nodes[channel['node1_pub']] = Node(name=channel['node1_pub'])
        if channel['node2_pub'] not in nodes: nodes[channel['node2_pub']] = Node(name=channel['node2_pub'])
        if channel["node1_policy"]:
            Channel.create_channel(node1=nodes[channel['node1_pub']],
                                   node2=nodes[channel['node2_pub']],
                                   base_fee=int(channel["node1_policy"]['fee_base_msat']),
                                   proportional_fee=int(channel["node1_policy"]['fee_rate_milli_msat']) / 1000.,
                                   delay=int(channel["node1_policy"]['time_lock_delta']),
                                   capacity=int(channel['capacity']),
                                   height=int(channel['channel_id']) >> 40,
                                   scid=channel['channel_id'].encode())
        if channel["node2_policy"]:
            Channel.create_channel(node1=nodes[channel['node1_pub']],
                                   node2=nodes[channel['node2_pub']], # TODO [to Alon] isnt the order of node1 node2 need to be switched?
                                   base_fee=int(channel["node2_policy"]['fee_base_msat']),
                                   proportional_fee=int(channel["node2_policy"]['fee_rate_milli_msat']) / 1000.,
                                   delay=int(channel["node2_policy"]['time_lock_delta']),
                                   capacity=int(channel['capacity']),
                                   height=int(channel['channel_id']) >> 40,
                                   scid=channel['channel_id'].encode())


    return nodes
