import csv
import time


class DataCollection:
    def __init__(self):
        self.data = []

    def log_event(self, event, value):
        self.data.append([time.time(), event, value])

    def save_to_csv(self):
        with open("game_data.csv", "w", newline="") as f:
            csv.writer(f).writerows([["time", "event", "value"]]+self.data)
