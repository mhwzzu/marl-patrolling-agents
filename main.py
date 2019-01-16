import os
from datetime import datetime
import time
import matplotlib.pyplot as plt
import torch
import numpy as np
from sim import Env, AgentDQN, ReplayMemory
from utils import Config, Metrics, compute_discounted_return

plt.ion()

config = Config('config/')

device_type = "cuda" if torch.cuda.is_available() and config.learning.cuda else "cpu"
device = torch.device(device_type)

print("Using", device_type)

model_path = os.path.abspath(config.learning.save_folder + '/' + datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
os.makedirs(model_path)

number_agents = config.agents.number_predators + config.agents.number_preys
# Definition of the agents
agents = [AgentDQN("predator", "predator-{}".format(k), device, config.agents)
          for k in range(config.agents.number_predators)]
agents += [AgentDQN("prey", "prey-{}".format(k), device, config.agents)
           for k in range(config.agents.number_preys)]

metrics = []

# Definition of the memories and set to device
# Define the metrics for all agents
for agent in agents:

    agent.memory = ReplayMemory(config.replay_memory.size)
    metrics.append(Metrics())

    # If we have to load the pretrained model
    if config.learning.use_model:
        path = os.path.abspath(os.path.join(config.learning.model_path, agent.id + ".pth"))
        agent.load(path)

env = Env(config.env)

# Add agents to the environment
for agent in agents:
    env.add_agent(agent, position=None)

fig_board = plt.figure(0)
ax_board = fig_board.gca()

fig_losses_returns, (ax_losses, ax_returns) = plt.subplots(1, 2)

plt.show()

start = time.time()
for episode in range(config.learning.n_episodes):
    test_step = False
    if not episode % config.learning.plot_episodes_every:
        test_step = True
    all_rewards = []
    states = env.reset()
    terminal = False
    while not terminal:
        actions = [agents[i].draw_action(states[i], no_exploration=test_step) for i in range(len(agents))]
        next_states, rewards, terminal = env.step(states, actions)
        all_rewards.append(rewards)

        if not episode % config.learning.plot_episodes_every:
            # Plot environment
            ax_board.cla()
            env.plot(next_states, rewards, ax_board)
            plt.draw()
            plt.pause(0.01)

        # Learning Step
        if not test_step:
            for k in range(len(agents)):
                # Add to agent memory
                agents[k].memory.add(states[k], next_states[k], actions[k], rewards[k])
                # Get batch for learning
                batch = agents[k].memory.get_batch(config.learning.batch_size, shuffle=config.replay_memory.shuffle)
                # Learn
                if batch is not None:
                    loss = agents[k].learn(batch)
                    metrics[k].add_loss(loss)

        states = next_states

    # Compute discounted return of the episode
    for k in range(len(agents)):
        reward = [all_rewards[i][k] for i in range(len(all_rewards))]
        discounted_return = compute_discounted_return(config.agents.gamma, reward)
        metrics[k].add_return(discounted_return)

    # Plot learning curves
    if not episode % config.learning.plot_curves_every:
        print("Episode", episode)
        print("Time :", time.time()-start)

        ax_losses.cla()
        ax_returns.cla()
        for k in range(len(agents)):
            # Compute average of losses of all learning step in episode and add it to the list of losses
            metrics[k].compute_averages()

            metrics[k].plot_losses(ax_losses, legend=agents[k].id)
            metrics[k].plot_returns(ax_returns, legend=agents[k].id)
        plt.legend()
        plt.draw()
        plt.pause(0.0001)

    # Save models
    for agent in agents:
        path = os.path.join(model_path, agent.id + ".pth")
        agent.save(path)
