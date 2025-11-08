import os
import json

LOCATION_COORDS = {
    'Farm': (0, 0),
    'Arcade': (10, 0),
    'Art Studio': (20, 0),
    'Beach': (30, 0),
    'Bridge': (40, 0),
    "Cindersap Forest": (50, 0),
    'Cabin': (10, 10),
    "Carpenter's Shop": (20, 10),
    'Forest': (30, 10),
    'General Store': (40, 10),
    'Home': (50, 10),
    'JojaMart': (10, 20),
    'Library': (20, 20),
    'Mountain Lake': (30, 20),
    'Riverbank': (40, 20),
    'Saloon': (50, 20),
    'Skate Park': (10, 30),
    'Town Square': (20, 30),
}


class villager():
    '''A class to represent a villager in Stardew Valley.'''
    def __init__(self, name: str, birthday: int, giftPreferences: list[str], locationScheduleTimes: list[str], locationSchedule: list[str]):
        self.name = name
        self.birthday = birthday
        self.giftPreferences = giftPreferences
        # self.beenGifted1 = False
        # self.beenGifted2 = False
        self.visitedToday = False

        # locationScheduleTimes: list of time strings ("HH:MM") in chronological order
        # locationSchedule: parallel list of location names matching the times by index
        self.locationScheduleTimes = locationScheduleTimes
        self.locationSchedule = locationSchedule

    @staticmethod
    def _time_str_to_minutes(time_str: str) -> int:
        """Convert a time string "HH:MM" to minutes since midnight.

        Raises ValueError if the string is not well-formed.
        """
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid time string: {time_str}")
        h, m = int(parts[0]), int(parts[1])
        return h * 60 + m

    def location_at(self, time_str: str, default=None):
        """Return the villager's location at the given time ("HH:MM").

        Behavior:
        - Finds the most recent scheduled time that is <= the query time and returns
          the corresponding location.
        - If the query time is earlier than the first scheduled time, returns
          `default` (None by default).

        Example: with schedule_times ["06:00","09:00","13:00"] and
        schedule_locs ["Home","Town Square","Riverbank"]:
        - location_at("08:00") -> "Home"
        - location_at("09:00") -> "Town Square"
        - location_at("05:00") -> None
        """
        try:
            q_min = self._time_str_to_minutes(time_str)
        except ValueError:
            raise

        last_idx = None
        for idx, t in enumerate(self.locationScheduleTimes):
            try:
                t_min = self._time_str_to_minutes(t)
            except ValueError:
                # malformed schedule time: skip
                raise
            if t_min <= q_min:
                last_idx = idx
            else:
                break

        if last_idx is None:
            return default
        return self.locationSchedule[last_idx]

def createVillagerList(day: int, rainy: bool):
    '''Creates a list of villager objects with their gift preferences, birthdays and schedules.

    This function will pick, for the requested `day`, either the 'sunny' or 'rainy' schedule
    depending on the `rainy` flag and save only that mapping into each villager's
    `locationSchedule` as: { day: { time: location } }.
    '''
    villagerList: list[villager] = []

    villager_dir = os.path.join(os.path.dirname(__file__), "Villagers")
    for VillagerFile in os.listdir(villager_dir):
        file_path = os.path.join(villager_dir, VillagerFile)

        # Skip non-json files just in case
        if not VillagerFile.lower().endswith('.json'):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Warning: failed to parse {file_path}: {e}")
                exit(1)

        # Derive name from filename (remove extension)
        name = os.path.splitext(VillagerFile)[0]

        # Extract simple fields
        try:
            birthday = data.get('birthday')
        except Exception as e:
            print(f"Warning: failed to get birthday for {name}: {e}")
            exit(1)    
    
        try:
            gift_prefs = data.get('giftPreferences')
        except Exception as e:
            print(f"Warning: failed to get giftPreferences for {name}: {e}")
            exit(1)

        # Parse schedule and pick only the chosen weather for the requested day.
        try: 
            raw_schedule = data.get('schedule')
        except Exception as e:
            print(f"Warning: failed to get schedule for {name}: {e}")
            exit(1)

        # We'll store the schedule as two parallel lists that can be indexed by position
        # - parsedScheduleTimes: list of time strings (e.g. "06:00") in chronological order
        # - parsedSchedule: list of location strings matching the times list by index
        parsedScheduleTimes: list[str] = []
        parsedSchedule: list[str] = []

        # Normalize day lookup (JSON keys are strings)
        day_key_str = str(day)
        day_val = raw_schedule.get(day_key_str) or raw_schedule.get(day)
        if isinstance(day_val, dict):
            weather_key = 'rainy' if rainy else 'sunny'
            times = day_val.get(weather_key) or {}
            if isinstance(times, dict):
                # times is a mapping time_str -> location. Convert it into two parallel
                # lists (times, locations) sorted by time so we can index by position later.
                for time_str, loc in sorted(times.items(), key=lambda x: x[0]):
                    parsedScheduleTimes.append(time_str)
                    parsedSchedule.append(loc)
            else:
                raise(KeyError(f"Weather '{weather_key}' schedule for day {day} not found in schedule for villager {name}"))
        else:
            raise(KeyError(f"Day {day} not found in schedule for villager {name}"))

        v = villager(name=name, birthday=birthday, giftPreferences=gift_prefs, locationScheduleTimes=parsedScheduleTimes, locationSchedule=parsedSchedule)
        villagerList.append(v)

    # villagerList is a list of all the villager objects that we can iterate over later and pass to the calculate_path function
    return villagerList

def calculate_path(currentLocationX, currentLocationY, currentTime, villagers: list[villager], currentPath: list = []):
    '''Calculates the optimal path to gift villagers based on their locations and gift preferences.'''
    path = []

    #PHILOSOPHY: at any moment, it makes sense to go to the location that will net us the most points for the least amount of time/ distance traveled.
    #While in theory it is be better to plan out every possible path ahead of time and choose the best, the complexity of that is too high for this project.
    #Instead, we will use a greedy algorithm to choose the next best location to go to based on the current time and location.

    #NOTE: The best path may actually be the one that simply has the farmer go to the closest villager next, as time is of the essence in Stardew Valley.
    #this means that doing it this way may actually be close to optimal, if not better because you probably value getting done gifting early more than being completely efficient.

    #TODO: starting at start location , calculate the distance to each other location and weight them (farther = less points, closer = more points)

    #analyze each location based on villagers that will be in/ around that location at that time, ignore villagers that have already been gifted today

    #add score to that location based on how many villagers are at that location

    #choose the location with the highest score, add it to the path, update current location to that location, mark all villagers there as visited today

    #update current time based on distance traveled to that location + (VERY IMPORTANT) giftingConstant to account for time spent gifting villagers at that location, plus
    #  any time spent waiting for villagers to show up if we arrive early, or otherwise time wasted (We are not robots, mistakes with be made)

    #repeat until all villagers have been gifted or time runs out

    return path





if __name__ == '__main__':
    # quick smoke test when running the script directly
    villagers = createVillagerList(1, False)
    print(f"Loaded {len(villagers)} villagers:")
    for villager in villagers:
        print(f"- {villager.name}: birthday={villager.birthday}, gifts={villager.giftPreferences}, schedule_times={villager.locationScheduleTimes}, schedule_locs={villager.locationSchedule}")
        print(f"  Location at 15:30: {villager.location_at('15:30')}")