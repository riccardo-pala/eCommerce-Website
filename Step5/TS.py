﻿import numpy as np

from Learner import Learner
from Environment import Environment, RoundData


class TS(Learner):

    def __init__(self, env: Environment):
        super().__init__(env)
        self.beta_parameters = np.ones((self.n_products, self.n_arms, 2))

    def update(self, results: RoundData):
        configuration = results.configuration
        idxs = np.arange(self.n_products)
        self.beta_parameters[idxs, configuration, 0] += results.conversions
        self.beta_parameters[idxs, configuration, 1] += results.visits - results.conversions
        self.update_estimates(configuration, results)

    def sample(self):
        return np.random.beta(self.beta_parameters[:, :, 0], self.beta_parameters[:, :, 1])

    def get_means(self):
        return self.beta_parameters[:, :, 0] / (self.beta_parameters[:, :, 0] + self.beta_parameters[:, :, 1])
