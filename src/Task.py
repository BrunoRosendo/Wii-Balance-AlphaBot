class Task:
    def __init__(self, func, delay, period):
        self.func = func
        self.delay = delay
        self.period = period
        self.counter = 0
