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
    def __init__(self, name: str, birthday: int | None = None, giftPreferences: list[str] | None = None, locationSchedule: dict | None = None):
        self.name = name
        self.birthday = birthday
        self.giftPreferences = giftPreferences or []
        # self.beenGifted1 = False
        # self.beenGifted2 = False
        self.visitedToday = False

    # locationSchedule will be a mapping for the chosen day: { time(str): location(str) }
        self.locationSchedule = locationSchedule or {}

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
                continue

        # Derive name from filename (remove extension)
        name = os.path.splitext(VillagerFile)[0]

        # Extract simple fields
        birthday = data.get('birthday')
        gift_prefs = data.get('gift_preferences') or data.get('giftPreferences') or []

        # Parse schedule and pick only the chosen weather for the requested day.
        raw_schedule = data.get('schedule') or {}
        parsed_schedule: dict[str, str] = {}

        # Normalize day lookup (JSON keys are strings)
        day_key_str = str(day)
        day_val = raw_schedule.get(day_key_str) or raw_schedule.get(day)
        if isinstance(day_val, dict):
            weather_key = 'rainy' if rainy else 'sunny'
            times = day_val.get(weather_key) or {}
            if isinstance(times, dict):
                # Save only the mapping time -> location for this day
                parsed_schedule = dict(times)
            else:
                raise(KeyError(f"Weather '{weather_key}' schedule for day {day} not found in schedule for villager {name}"))
        else:
            raise(KeyError(f"Day {day} not found in schedule for villager {name}"))

        v = villager(name=name, birthday=birthday, giftPreferences=gift_prefs, locationSchedule=parsed_schedule)
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
        print(f"- {villager.name}: birthday={villager.birthday}, gifts={villager.giftPreferences}, schedule_times={sorted(list(villager.locationSchedule.keys()))}")