import numpy as np
from Learner import Learner
from NonStationaryEnvironment import NonStationaryEnvironment, RoundData


class SW_UCB(Learner):

    def __init__(self, env: NonStationaryEnvironment, window_size=31):
        super().__init__(env)
        self.t = 0
        self.confidence = np.ones((self.n_products, self.n_arms)) * np.inf
        self.empirical_means = np.zeros((self.n_products, self.n_arms))
        self.c = 0.2
        self.window_size = window_size
        self.pulled_arms_timeline = []
        self.pulled_rounds = np.zeros((self.n_products, self.n_arms))
        self.rewards_per_arms = [[[] for _ in range(self.n_arms)] for _ in range(self.n_products)]

    def pull(self):
        exp_conversion_rates = self.sample()
        alpha_ratios = np.array([self.get_expected_alpha_ratios()[:self.n_products]] * self.n_arms).transpose()
        exp_rewards = \
            (exp_conversion_rates * self.prices * self.avg_products_sold + self.marginal_rewards) * alpha_ratios
        configuration = np.argmax(exp_rewards, axis=1)
        return configuration

    def update(self, results: RoundData):
        self.t += 1
        configuration = results.configuration  # pulled arms during last round
        conversion_rates = results.conversions / results.visits
        self.pulled_arms_timeline.append(configuration)  # to store pulled arms in time
        for prod in range(self.n_products):
            for arm in range(self.n_arms):
                self.rewards_per_arms[prod][configuration[prod]].append(conversion_rates[prod])  # shape n_prod X n_arms
        # select last window_size pulled configurations
        valid_configurations = np.array(self.pulled_arms_timeline[-self.window_size:])  # shape win_size X n_prod
        # np.bincount counts the number of times each arm has been pulled for each product
        self.pulled_rounds = np.array([np.bincount(pulls_per_prod, minlength=self.n_arms)  # shape n_prod X n_arms
                                       for pulls_per_prod in valid_configurations.T])
        for prod in range(self.n_products):
            for arm in range(self.n_arms):
                n = self.pulled_rounds[prod][arm]  # to select only valid rewards for update
                self.empirical_means[prod, arm] = np.sum(self.rewards_per_arms[prod][arm][-n:]) / n if n > 0 else 0
                self.confidence[prod, arm] = self.c * (np.log(self.t) / n) ** 0.5 if n > 0 else np.inf

    def sample(self):
        return self.empirical_means + self.confidence

    def get_means(self):
        return self.empirical_means
