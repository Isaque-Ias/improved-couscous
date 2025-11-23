import time

class Testing:
    _times = {}
    _temp = {}
    def_cap = 10

    @classmethod
    def set_perf_cap(cls, name, cap):
        if cls._times.get(name) == None:
            cls._times[name] = {"data": [], "cap": cap}
        else:
            cls._times[name]["cap"] = cap

    @classmethod
    def set_def_cap(cls, cap):
        cls._def_cap = cap
    @classmethod
    def tick_time_start(cls, name):
        cls._temp[name] = time.perf_counter()

    @classmethod
    def tick_time_end(cls, name):
        end = time.perf_counter()
        start = cls._temp[name]

        if cls._times.get(name) == None:
            cls._times[name] = {"data": [], "cap": cls._def_cap}

        if len(cls._times[name]["data"]) >= cls._times[name]["cap"]:
            cls._times[name]["data"].pop(0)

        cls._times[name]["data"].append(end - start)
        
        cls._temp.pop(name)

    @classmethod
    def get_average(cls, name):
        return sum(cls._times[name]["data"]) / len(cls._times[name]["data"])
    
    @classmethod
    def get_relatory(cls):
        if len(cls._times) == 0:
            return "No timings were made."
        message = ""
        for key in cls._times.keys():
            message = message + f"{format(cls.get_average(key), ".20f")} seconds on \"{key}\" in {cls._times[key]["cap"]} tries.\n"

        return message