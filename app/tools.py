class Tools:
    @classmethod
    def binary_search(cls, value, list, list_len, func=lambda x: x, index=0):
        if list_len == 0:
            return index
        
        mid_index = list_len // 2
        mid_value = func(list[mid_index])
        
        if mid_value == value:
            return index + mid_index
        
        if value > mid_value:
            return cls.binary_search(value, list[mid_index + 1:], list_len - mid_index - 1, func, index + mid_index + 1)
        else:
            return cls.binary_search(value, list[:mid_index], mid_index, func, index)