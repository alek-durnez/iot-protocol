import time


class Battery:
    def __init__(self, initial_capacity=100.0, drain_idle=0.05, drain_tx=2.0):
        self.capacity = initial_capacity
        self.current = initial_capacity
        self.drain_idle = drain_idle  # Cost per second just to be alive
        self.drain_tx = drain_tx  # Cost to fire the radio (Expensive!)
        self.last_update = time.time()
        self.is_dead = False

    def update_idle(self):
        """Calculates background drain since last check."""
        if self.is_dead: return 0

        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now

        loss = elapsed * self.drain_idle
        self.current -= loss
        self.check_death()
        return self.current

    def consume_tx(self, retries=0):
        """Instant battery hit for using the radio."""
        if self.is_dead: return

        # Base cost + cost for every retry
        total_cost = self.drain_tx + (retries * (self.drain_tx * 0.5))
        self.current -= total_cost
        self.check_death()

    def check_death(self):
        if self.current <= 0:
            self.current = 0
            self.is_dead = True