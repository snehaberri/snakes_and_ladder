import random

class ladder:
    def __init__(self):
        self.ladders ={}
    def get_height_range(self, start):
        if start <= 20:
            return (8,15)
        elif start<=40:
            return (10,20)
        elif start <=60:
            return (6,14)
        elif start <=80:
            return (4,10)
        else:
            return (2,6)
    
    def generate_ladders(self, count, occupied):
        self.ladders.clear()
        
        while len(self.ladders)<count:
            start = random.randint(2,90)
            if start in occupied:
                continue
            
            min_h, max_h= self.get_height_range(start)
            end = start+ random.randint(min_h, max_h)
            if end >100 or end in occupied:
                continue
            
            self.ladders[start]= end
            occupied.add(start)
            occupied.add(end)
            
        return self.ladders
    def check_ladder(self,tile):
        return self.ladders.get(tile)
            
        