class PoolBall():
    def __init__(self,isStripe: bool,number: int):
        self.number = number
        self.isStripe = isStripe
        self.inHole = False

    def hole(self):
        if not self.inHole:
            print(f'Ball {self.number} still on the table')
        else:
            print(f'Ball {self.number} in the hole ')










Number8 = PoolBall(False,8)
Number8.hole()
