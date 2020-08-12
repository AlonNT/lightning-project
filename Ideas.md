# General Insights, Ideas & Questions
## References
- Hijacking Routes in Payment Channel Networks: A Predictability Tradeoff
   - [paper](https://arxiv.org/pdf/1909.06890.pdf)
   - [medium post](https://medium.com/blockchains-huji/route-hijacking-and-dos-in-off-chain-networks-37ce6f54aa26)
   - [code](https://github.cs.huji.ac.il/saart/saart-lightning)
- Congestion Attacks in Payment Channel Networks
   - [paper](https://arxiv.org/pdf/2002.06564.pdf)
   - [medium post](https://medium.com/blockchains-huji/congestion-attacks-in-payment-channel-networks-b7ac37208389)
   - [code](https://github.com/ayeletmz/Lightning-Network-Congestion-Attacks)
- Flood & Loot: A Systemic Attack On The Lightning Network
   - [paper](https://arxiv.org/pdf/2006.08513.pdf)
   - [medium post](https://medium.com/blockchains-huji/flood-loot-a-systemic-attack-on-the-lightning-network-5c3dac7bba24)
   - [code](https://github.com/jonahar/lightning-systemic-attack)
- [Coindesk: You can now get paid (a little) for using bitcoin’s lightning network.](https://www.coindesk.com/you-can-now-get-paid-a-little-for-using-bitcoins-lightning-network)
- [Lightning network: how to explore the topology](https://medium.com/coinmonks/lightning-network-how-to-explore-the-topology-32f234f4287f)
- [Basis of Lightning Technology (BOLT)](https://github.com/lightningnetwork/lightning-rfc/blob/master/00-introduction.md)
- [1ML - Lightning Network Search and Analysis Engine](https://1ml.com/)
- [Bitcoin Explorer - Blockstream.info](https://blockstream.info/)

#### Python Packages
- [NetworkX](https://networkx.github.io/documentation/latest/tutorial.html)

## Questions
- How do nodes in the Lightning network discover the structure of the network's graph?
  - This includes the nodes, channels, and their capacities. 
  - When does this information updated?
    - Foe example, assume some new node joins the network and connects to several other nodes. When will the entire
      network will be aware of its existence? A quote from the paper
      ```text
      ...
      In order to find such a path, nodes leverage the knowledge
      of the channel graph which is continuously gossiped about by
      nodes in the network. Given this knowledge of the network
      graph, nodes utilize source routing to pick their path.
      ...
      ```
  - [Answer](https://bitcoin.stackexchange.com/questions/87585/how-do-new-nodes-learn-the-topology-of-lightning-network)

