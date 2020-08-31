# Maximizing Revenue in The Lightning-Network
### Alon Netser, Ariel Elnekave & Daniel Afrimi

<img align="right" width="300" height="200" src="https://github.com/AlonNT/lightning-project/blob/master/Paper/images/lightning.jpg">
## Introduction

The Lightning Network has been suggested as a solution to Bitcoin’s long-known scalability issues. The Lightning Network promises to improve both the number of transactions that can be processed, and the latency per transaction. The Lightning Network, along with other payment channel networks, aims to move the majority of transactions off-chain, with the guarantee that the state of channels can be committed back to the blockchain at any time, in a trustless fashion. It thus solves the problem of a limited transaction rate by limiting the communication on payments to a much smaller set of participants, and lowers the number of interactions with the blockchain.

An important feature of payment channel networks is that they also support transactions between participants without a direct channel between them, using multi-hop routing. In order to incentivize participating in other parties transactions, intermediate nodes may require fees for transferring the money forwards to the next node in the route. 

## Our Work
In this work we analyze the potential revenue in creating channels in the Lightning Network. The amount of money we lock in channels is treated as an investment. Our cost of investing in the Lightning Network includes both the locked money in the channels, as well as the fees to pay the miners to include the channel's creation transaction in the blockchain. Indeed, traditional investments (e.g. stocks, real-estate) are made by locking money in order to maximize the yield and minimize the risk, and there are also side payments such as fees to mediators, so our methodology falls into this framework.

We analyze different policies (a.k.a. agents) which all aim to maximize the profit gained from the fees. The main challenge is deciding which channels to create and how much money to lock in them, in order to be attractive for other parties to route transactions through them.

## Methods

### Random Agent

This one is the simplest algorithm, used mainly as a baseline for other more sophisticated ones. Given the input parameter $d$, the random agent opens $d$ channels with $d$ nodes selected uniformly at random from the graph, where its initial funds are evenly divided between the channels. The fee policy of each channel it created is the default policy.

### Greedy

We defined three methods for scoring the nodes, each score define a corresponding greedy algorithm. The greedy algorithm orders the nodes in a descending/ascending order according to their score, and then choose the first d nodes (where d is an input parameter) and establish channels with them dividing its funds equally between the channels. The fee policy of each channel it creates is the default policy. \\
The scoring methods are the following:

- Channel capacity: 
Each node's score is its total capacity - the sum of the capacities in all of the channels it's participating in.
- Graph-Degree: 
Each node's score is its degree in the multi-graph.
- Routeness:
Each node's score is the number of routes it might participate in, when some two nodes in the graph will make a transaction.

### Lightning++

The motivation for this algorithm is taken from kmeans++ clustering algorithm, and this is where it got its name. In the traditional kmeans clustering algorithm the initial centroids are chosen uniformly at random. In kmeans++ the initial centroids are sampled according to a distribution which gives high probability to nodes that are distant from the previously selected centroids. This enables choosing the initial centroids in a random way which results in nodes that are far from each other (which helps the algorithm to cluster better), ignoring outliers which are a few data-points that are extremely far from the rest.

We wanted to add randomness to our agents policies, so instead of selecting greedily the best node (according to some ordering), we define a distribution over the nodes where each node probability is according to its score - higher score implies higher probability to select this node. Eventually the Lightning++ agent works similar to the greedy agent, meaning that it selects nodes with high rank according to some score function, but it does so in a random way so not always the "best" node will be selected.



Read More - [Maximizing Revenue in The Lightning-Network](https://github.cs.huji.ac.il/daniel023/GLANN-For-Video/blob/master/Non-Adversarial%20Video%20Synthesis%20with%20Generative%20Latent%20Nearest%20Neighbors.pdf)
# TODO Change the link in the readme to our paper
