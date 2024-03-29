from NonStationaryEnvironment import RoundData


class CUMSUM:

    def __init__(self, M, eps, h):
        self.M = M  # first samples to calculate the reference point
        self.eps = eps  # epsilon is in the formula of the deviation from the reference
        self.h = h  # upper and lower bound for an abrupt change
        self.reference = 0  # reference is the empirical mean over the first M samples
        self.t = 0
        self.g_plus = 0  # cumulative positive deviation of an arm until time t
        self.g_minus = 0  # cumulative negative deviation of an arm until time t

    def update(self, data: RoundData, arm):
        self.t += 1
        if self.t <= self.M:
            self.reference += (data.conversions[arm] / data.visits[arm]) / self.M  # warm up to compute the reference
            return 0
        else:
            # Positive and negative deviation from the reference point
            s_plus = ((data.conversions[arm] / data.visits[arm]) - self.reference) - self.eps
            s_minus = -((data.conversions[arm] / data.visits[arm]) - self.reference) - self.eps
            self.g_plus = max(0, self.g_plus + s_plus)
            self.g_minus = max(0, self.g_minus + s_minus)
            return self.g_plus > self.h or self.g_minus > self.h  # True if a change is detected

    def reset(self):
        self.t = 0
        self.g_plus = 0
        self.g_minus = 0
