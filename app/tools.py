class Tools:
    @classmethod
    def binary_search(cls, value, list, func=lambda x: x):
        left = 0
        right = len(list)

        while left < right:
            mid = (left + right) // 2
            mid_value = func(list[mid])

            if mid_value == value:
                return mid
            elif mid_value < value:
                left = mid + 1
            else:
                right = mid

        return left
        
    @staticmethod
    def clamp(a, b, v):
        return min(b, max(a, v))