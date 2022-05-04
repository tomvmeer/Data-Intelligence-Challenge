import copy
import random

import numpy as np

SMALL_ENOUGH = 1e-3
#ALL_POSSIBLE_ACTIONS = ('U', 'D', 'L', 'R')
orients = {'n': -3, 'e': -4, 's': -5, 'w': -6}
dirs = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}

class Robot:
    def __init__(self, grid, pos, orientation, p_move=0, battery_drain_p=0, battery_drain_lam=0, vision=1):
        if grid.cells[pos[0], pos[1]] != 1:
            raise ValueError
        self.orientation = orientation
        self.pos = pos
        self.grid = grid
        self.orients = {'n': -3, 'e': -4, 's': -5, 'w': -6}
        self.dirs = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}
        self.grid.cells[pos] = self.orients[self.orientation]
        self.history = [[], []]
        self.p_move = p_move
        self.battery_drain_p = battery_drain_p
        self.battery_drain_lam = battery_drain_lam
        self.battery_lvl = 100
        self.alive = True
        self.vision = vision

    def possible_tiles_after_move(self):
        moves = list(dirs.values())
        # Fool the robot and show a death tile as normal (dirty)
        data = {}
        for i in range(self.vision):
            for move in moves:
                to_check = tuple(np.array(self.pos) + (np.array(move) * (i + 1)))
                if to_check[0] < self.grid.cells.shape[0] and to_check[1] < self.grid.cells.shape[1] and to_check[
                    0] >= 0 and to_check[1] >= 0:
                    data[tuple(np.array(move) * (i + 1))] = self.grid.cells[to_check]
                    # Show death tiles as dirty:
                    if data[tuple(np.array(move) * (i + 1))] == 3:
                        data[tuple(np.array(move) * (i + 1))] = 1
        return data

    def move(self):
        # Can't move if we're dead now, can we?
        if not self.alive:
            return False
        random_move = np.random.binomial(1, self.p_move)
        do_battery_drain = np.random.binomial(1, self.battery_drain_p)
        if do_battery_drain == 1 and self.battery_lvl > 0:
            self.battery_lvl -= np.random.exponential(self.battery_drain_lam)
        # Handle empty battery:
        if self.battery_lvl <= 0:
            self.alive = False
            return False
        if random_move == 1:
            moves = self.possible_tiles_after_move()
            random_move = random.choice([move for move in moves if moves[move] >= 0])
            new_pos = tuple(np.array(self.pos) + random_move)
            # Only move to non-blocked tiles:
            if self.grid.cells[new_pos] >= 0:
                new_orient = list(self.dirs.keys())[list(self.dirs.values()).index(random_move)]
                tile_after_move = self.grid.cells[new_pos]
                self.grid.cells[self.pos] = 0
                self.grid.cells[new_pos] = self.orients[new_orient]
                self.pos = new_pos
                self.history[0].append(self.pos[0])
                self.history[1].append(self.pos[1])
                if tile_after_move == 3:
                    self.alive = False
                    return False
                return True
            else:
                return False
        else:
            new_pos = tuple(np.array(self.pos) + self.dirs[self.orientation])
            # Only move to non-blocked tiles:
            if self.grid.cells[new_pos] >= 0:
                tile_after_move = self.grid.cells[new_pos]
                self.grid.cells[self.pos] = 0
                self.grid.cells[new_pos] = self.orients[self.orientation]
                self.pos = new_pos
                self.history[0].append(self.pos[0])
                self.history[1].append(self.pos[1])
                # Death:
                if tile_after_move == 3:
                    self.alive = False
                    return False
                return True
            else:
                return False

    def move_to_position(self):
        # Can't move if we're dead now, can we?
        if not self.alive:
            return False
        new_pos = tuple(np.array(self.pos) + self.dirs[self.orientation])
        # Only move to non-blocked tiles:
        if self.grid.cells[new_pos] >= 0:
            tile_after_move = self.grid.cells[new_pos]
            self.grid.cells[self.pos] = 0
            self.grid.cells[new_pos] = self.orients[self.orientation]
            self.pos = new_pos
            self.history[0].append(self.pos[0])
            self.history[1].append(self.pos[1])
            # Death:
            if tile_after_move == 3:
                self.alive = False
                return False
            return True
        else:
            return False

    def rotate(self, dir):
        current = list(self.orients.keys()).index(self.orientation)
        if dir == 'r':
            self.orientation = list(self.orients.keys())[(current + 1) % 4]
        elif dir == 'l':
            self.orientation = list(self.orients.keys())[current - 1]
        self.grid.cells[self.pos] = self.orients[self.orientation]


class Grid:
    def __init__(self, n_cols, n_rows):
        self.n_rows = n_rows
        self.n_cols = n_cols
        # Building the boundary of the grid:
        self.cells = np.ones((n_cols, n_rows))
        self.cells[0, :] = self.cells[-1, :] = -1
        self.cells[:, 0] = self.cells[:, -1] = -1

    def put_obstacle(self, x0, x1, y0, y1, from_edge=1):
        self.cells[max(x0, from_edge):min(x1 + 1, self.n_cols - from_edge),
        max(y0, from_edge):min(y1 + 1, self.n_rows - from_edge)] = -2

    def put_singular_obstacle(self, x, y):
        self.cells[x][y] = -2

    def put_singular_goal(self, x, y):
        self.cells[x][y] = 2

    def put_singular_death(self, x, y):
        self.cells[x][y] = 3


def generate_grid(n_cols, n_rows):
    # Placeholder function used to generate a grid.
    # Select an empty grid file in the user interface and add code her to automatically fill it.
    # Look at grid_generator.py for inspiration.
    grid = Grid(n_cols, n_rows)
    return grid


class State:
    def __init__(self, grid, pos, orientation, p_move=0, battery_drain_p=0, battery_drain_lam=0):
        # if grid.cells[pos[0], pos[1]] != 1:
        #     raise ValueError
        self.orientation = orientation
        self.pos = pos
        self.grid = grid
        #self.grid.cells[pos] = orients[self.orientation]
        self.p_move = p_move
        self.alive = True
        self.battery_drain_p = battery_drain_p
        self.battery_drain_lam = battery_drain_lam

    # def move(self):
    #     # Can't move if we're dead now, can we?
    #     if not self.alive:
    #         return False
    #     new_pos = tuple(np.array(self.pos) + dirs[self.orientation])
    #     # Only move to non-blocked tiles:
    #     if self.grid.cells[new_pos] >= 0:
    #         tile_after_move = self.grid.cells[new_pos]
    #         self.grid.cells[self.pos] = 0
    #         self.grid.cells[new_pos] = orients[self.orientation]
    #         self.pos = new_pos
    #         # Death:
    #         if tile_after_move == 3:
    #             self.alive = False
    #             return False
    #         return True
    #     else:
    #         return False

    def rotate(self, curr_dir):
        current = list(orients.keys()).index(self.orientation)
        if curr_dir == 'r':
            self.orientation = list(orients.keys())[(current + 1) % 4]
        elif curr_dir == 'l':
            self.orientation = list(orients.keys())[current - 1]
        #self.grid.cells[self.pos] = orients[self.orientation]



    def get_possible_moves(self):
        data = {}
        moves = list(dirs.values())
        i = 1
        for move in moves:
            to_check = tuple(np.array(self.pos) + (np.array(move) * (i + 1)))
            if to_check[0] < self.grid.cells.shape[0] and to_check[1] < self.grid.cells.shape[1] and to_check[
                0] >= 0 and to_check[1] >= 0:
                data[tuple(np.array(move) * (i + 1))] = self.grid.cells[to_check]
                # Show death tiles as dirty:
                if data[tuple(np.array(move) * (i + 1))] == 3:
                    data[tuple(np.array(move) * (i + 1))] = 1
        return data

    def get_reward(self):
        reward_dict = {
            -2: -2,
            -1: -2,
            0: -1,
            1: 1,
            2: 10,
            3: -10
        }
        state_reward = reward_dict[self.grid.cells[self.pos]]

        # modified from environment.py
        # TODO: correct?
        expected_drain = self.battery_drain_p * np.random.exponential(self.battery_drain_lam)

        # reward is reward of moving to new state + expected battery drain (negative constant)
        reward = state_reward - expected_drain

        return reward

    def get_neighbouring_states(self): # Checks neighboring state is not a wall/obstacle
        if not self.alive: #at death state
            return []
        moves = list(dirs.values())
        states = []
        for move in moves:
            new_pos = tuple(np.array(self.pos) + np.array(move))
            if new_pos[0] < self.grid.cells.shape[0] and new_pos[1] < self.grid.cells.shape[1] and \
                    new_pos[0] >= 0 and new_pos[1] >= 0 and self.grid.cells[new_pos] >=0:
                new_state = copy.deepcopy(self)
                # Find out how we should orient ourselves:
                new_orient = list(dirs.keys())[list(dirs.values()).index(move)]
                # Orient ourselves towards the dirty tile:
                while new_orient != new_state.orientation:
                    # If we don't have the wanted orientation, rotate clockwise until we do:
                    # print('Rotating right once.')
                    new_state.rotate('r')

                # Only move to non-blocked tiles:
                if new_state.grid.cells[new_pos] >= 0:
                    tile_after_move = new_state.grid.cells[new_pos]
                    if tile_after_move == 3:
                        new_state.alive = False
                    else:
                        new_state.grid.cells[new_state.pos] = 0
                    #new_state.grid.cells[new_pos] = new_state.orients[new_state.orientation]
                    new_state.pos = new_pos

                    states.append(new_state)
        return states

    def get_action_reward(self, action):
        state_primes = self.get_neighbouring_states() # Excludes obstacles and walls
        transitions = []
        new_pos = tuple(np.array(self.pos) + dirs[action])

        # Getting the transition probabilities
        for state_prime in state_primes:
            if state_prime.pos == new_pos:
                prob = 1 - state_prime.p_move
            elif state_prime.p_move == 0:
                prob = 0
            else:
                prob = state_prime.p_move/(len(state_primes)-1)
            transitions.append((prob, state_prime.get_reward(), state_prime))
        return transitions


def is_terminal(state):

    if not state.alive:
        return True
    g = state.grid.cells
    # TODO: consider unreachable situations
    return not np.isin(g, [1, 2]).any()


def best_action_value(V, s, gamma):
    # finds the highest value action (max_a) from state s, returns the action and value
    best_a = None
    best_value = float('-inf')

    # loop through all possible actions to find the best current action
    for a in dirs.keys():
        state_primes = s.get_action_reward(a)
        sum_a = 0
        for (prob, r, state_prime) in state_primes:
            state_prime_value = 0
            if (str(state_prime.grid.cells), state_prime.pos) in V:
                state_prime_value = V[(str(state_prime.grid.cells), state_prime.pos)]

            sum_a += prob * (r + (gamma * state_prime_value))

        v = sum_a
        if v > best_value:
            best_value = v
            best_a = a
    return best_a, best_value


def evaluate_state(state, V, gamma, all_states):
    if is_terminal(state):
        print("REACHED terminal state", (str(state.grid.cells), state.pos))
        return V

    best_a, best_val = best_action_value(V, state, gamma)
    V[(str(state.grid.cells), state.pos)] = best_val
    all_states[(str(state.grid.cells), state.pos)] = state
    for new_state in state.get_neighbouring_states():
        if not (str(new_state.grid.cells), new_state.pos) in V:
            V = evaluate_state(new_state, V, gamma, all_states)
    return V


class SmartRobot(Robot):
    def __init__(self, grid, pos, orientation, p_move=0, battery_drain_p=0, battery_drain_lam=0, vision=1, gamma=0.9):
        if grid.cells[pos[0], pos[1]] != 1:
            raise ValueError
        self.orientation = orientation
        self.pos = pos
        self.grid = grid
        self.orients = {'n': -3, 'e': -4, 's': -5, 'w': -6}
        self.dirs = {'n': (0, -1), 'e': (1, 0), 's': (0, 1), 'w': (-1, 0)}
        #self.grid.cells[pos] = self.orients[self.orientation]
        self.history = [[], []]
        self.p_move = p_move
        self.battery_drain_p = battery_drain_p
        self.battery_drain_lam = battery_drain_lam
        self.battery_lvl = 100
        self.alive = True
        self.vision = vision
        self.gamma = gamma
        self.V = self.calculate_values()
        # self.policy = self.calculate_policy()


    def calculate_values(self):
        print("Start calculating V ")
        current_state = State(self.grid, self.pos, self.orientation, self.p_move, self.battery_drain_p,
                              self.battery_drain_lam)
        V = {}
        all_states = {}

        V = evaluate_state(current_state, V, self.gamma, all_states)
        print("robot.v count:", len(V.keys()))
        print("robot.all_states count:", len(all_states.keys()))
        biggest_change = np.inf
        iteration_counter = 0
        biggest_change_state = current_state
        while biggest_change > SMALL_ENOUGH:
            biggest_change = 0
            for s in all_states.values():
                old_v = V[(str(s.grid.cells), s.pos)]
                _, new_v = best_action_value(V, s, self.gamma)
                V[(str(s.grid.cells), s.pos)] = new_v

                if (np.abs(old_v - new_v) > biggest_change):
                    biggest_change = np.abs(old_v - new_v)
                    biggest_change_state = (str(s.grid.cells), s.pos)
                    #biggest_change = max(biggest_change, np.abs(old_v - new_v))
            iteration_counter+=1
            print("iteration:", iteration_counter, "biggest_change:", biggest_change, "state:",biggest_change_state)
        return V



    # def calculate_policy(self):
    #     current_state = State(self.grid, self.pos, self.orientation, self.p_move, self.battery_drain_p,
    #                           self.battery_drain_lam)
    #     possible_states = current_state.get_possible_states()
    #     policy = {}
    #     # find a policy that leads to optimal value function
    #     for s in possible_states:
    #         # loop through all possible actions to find the best current action
    #         best_a, _ = best_action_value(self.V, s)
    #         policy[(s.grid.cells, s.pos)] = best_a
    #     return policy

#{(grid, pos): best_a, }
