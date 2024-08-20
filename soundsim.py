import math
import numpy as np

def get_2D_normal_vec(vec):
    return np.array([-vec[1], vec[0]])

class Envinronment:

    def __init__(self, n_teams, n_signals, field_shape):
    
        self.n_teams = n_teams
        self.field_w = field_shape[0] # Width
        self.field_h = field_shape[1] # Height
    
        self.entities = {"epuck_teams": [], "signals": []}



class Epuck:

    def __init__(self, init_pos, init_ori):
        self.pos = init_pos
        self.ori = init_ori/180 * math.pi

        self.relative_micro_positions = [np.array([-0.2, 0]), np.array([0.2, 0]), np.array([0, 0.1])]
        self.micro_positions = []
        self.update_microphone_positions()

    def get_facing_direction(self):
        return np.array([math.cos(self.ori[0]), math.sin(self.ori[1])])

    def move(self, length, d_ori):
        self.ori += d_ori
        self.pos += length * self.get_facing_direction()

    def update_microphone_positions(self):
        for i, microphone_relative_pos in enumerate(self.relative_micro_positions):
            self.micro_positions[i] = self.pos + self.get_facing_direction() * microphone_relative_pos

    def localize_sound(self, signal):

        L_0 = signal.calculate_signal_strength(self.micro_positions[0])
        L_1 = signal.calculate_signal_strength(self.micro_positions[1])
        L_2 = signal.calculate_signal_strength(self.micro_positions[2])

        base_01 = self.micro_positions[1] - self.micro_positions[0]
        h_01 = get_2D_normal_vec(base_01)

        base_02 = self.micro_positions[2] - self.micro_positions[0]
        h_02 = get_2D_normal_vec(base_02)

        base_12 =self.micro_positions[3] - self.micro_positions[2]
        h_12 = get_2D_normal_vec(base_12)


        c_01 = 1 if L_0 > L_1 else -1
        c_02 = 1 if L_0 > L_2 else -1
        c_12 = 1 if L_1 > L_2 else -1




class Signal:

    def __init__(self, position, strength_db):
        self.pos = position

        self.strength = strength_db
        self.w_x = 0.2
        self.w_y = 0.2
        self.dampening = 0

        self.r_0 = 1

    # clip to 10% of local strength
    def calculate_signal_noise(self, x, y, local_signal_strength):
        return max(-0.1, min(0.1, math.cos(self.w_x * x + self.w_y * y))) * local_signal_strength

    def calculate_signal_strength(self, position):

        r_epuck = 1/(np.linalg.norm(self.pos-position)**2)
        local_strength = self.strength - 10 * math.log10(self.r_0/r_epuck - self.dampening * r_epuck)

        return local_strength + self.calculate_signal_noise(local_strength)