def find_nearest_date(timestamps: list[int], pivot: int) -> int:
    return min(timestamps, key=lambda x: abs(x - pivot))
