import random

class Snake:
    def __init__(self):
        self.snakes = {}

    def get_drop_range(self, start):
        if start ==27:
            return (7,27)
        elif start == 57:
            return (16,57)
        elif start ==71:
            return (71,41)
        elif start ==75:
            return (10, 20)
        else:
            return (15, 25)

    def generate_snakes(self, count, occupied):
        self.snakes.clear()

        while len(self.snakes) < count:
            start = random.randint(10, 99)

            if start in occupied:
                continue

            min_d, max_d = self.get_drop_range(start)
            end = start - random.randint(min_d, max_d)

            if end < 1 or end in occupied:
                continue

            self.snakes[start] = end
            occupied.add(start)
            occupied.add(end)

        return self.snakes

    def check_snake(self, tile):
        return self.snakes.get(tile)
