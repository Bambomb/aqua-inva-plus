def map_range(x, in_min, in_max, out_min, out_max):
    return out_min + (((x - in_min) / (in_max - in_min)) * (out_max - out_min))