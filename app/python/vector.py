from math import cos, sin, degrees, atan2, pi

class VecN:
    def __init__(self, *values):
        self.scalars = values

    def magnitude(self):
        return sum(map(lambda x: x ** 2, self.scalars)) ** .5

    def magnitude_squared(self):
        return sum(map(lambda x: x ** 2, self.scalars))

    def normalize(self):
        magnitude = self.magnitude()
        return VecN(*map(lambda x: x / magnitude, self.scalars))
    
    def dot(self, other):
        products = [self.scalars[i] * other.scalars[i] for i in range(len(self.scalars))]
        return sum(products)

    def __add__(self, other):
        if isinstance(other, VecN):
            products = [self.scalars[i] + other.scalars[i] for i in range(len(self.scalars))]
        else:
            products = [self.scalars[i] + other[i] for i in range(len(self.scalars))]
        return VecN(*products)

    def __neg__(self):
        return VecN(*map(lambda x: -x, self.scalars))

    def __sub__(self, other):
        if isinstance(other, VecN):
            products = [self.scalars[i] - other.scalars[i] for i in range(len(self.scalars))]
        else:
            products = [self.scalars[i] - other[i] for i in range(len(self.scalars))]
        return VecN(*products)

    def __mul__(self, other):
        products = [self.scalars[i] * other for i in range(len(self.scalars))]
        return VecN(products)

    def __rmul__(self, other):
        products = [self.scalars[i] * other for i in range(len(self.scalars))]
        return VecN(products)
    
    def __truediv__(self, other):
        products = [self.scalars[i] / other for i in range(len(self.scalars))]
        return VecN(products)

    def __floordiv__(self, other):
        products = [self.scalars[i] // other for i in range(len(self.scalars))]
        return VecN(products)
    
    def unp(self):
        return tuple(*self.scalars)
    
    def __getitem__(self, index):
        if index > len(self.scalars) or index < 0:
            raise ValueError("Index fora da lista.")
        return self.scalars[index]

    def __repr__(self):
        return f'[{self.scalars}]'

class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def angle(self):
        ang = degrees(atan2(self.y, self.x))  # returns [-180, 180]
        if ang < 0:
            ang += 360
        return ang

    def rotate(self, angle):
        return Vec(self.x * cos(angle * pi / 180) - self.y * sin(angle * pi / 180),
                   self.x * sin(angle * pi / 180) + self.y * cos(angle * pi / 180))
    
    def rotate90(self):
        return Vec(self.y, -self.x)
    
    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** .5

    def magnitude_squared(self):
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        magnitude = self.magnitude()
        return Vec(self.x / magnitude, self.y / magnitude)
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def mirror_x(self):
        return Vec(-self.x, self.y)

    def mirror_y(self):
        return Vec(self.x, -self.y)

    def __add__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x + other.x, self.y + other.y)
        return Vec(self.x + other[0], self.y + other[1])

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __sub__(self, other):
        if isinstance(other, Vec):
            return Vec(self.x - other.x, self.y - other.y)
        return Vec(self.x + other[0], self.y + other[1])

    def __mul__(self, other):
        return Vec(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vec(self.x * other, self.y * other)
    
    def __truediv__(self, other):
        return Vec(self.x / other, self.y / other)

    def __floordiv__(self, other):
        return Vec(self.x // other, self.y // other)
    
    def unp(self):
        return (self.x, self.y)
    
    def __getitem__(self, index):
        if index > 1 or index < 0:
            raise ValueError("Index fora da lista.")
        return self.x if index == 0 else self.y

    def __repr__(self):
        return f'[{self.x}, {self.y}]'
