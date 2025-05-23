import calendar
import json
import os
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

ALLOWED_VALUES = ["no", "yes", "sick", "cancel"]
FILE_NAME = "trackedData.json"
ALLOW_ONE_SET = False

class Tracker:
    def __init__(self, name, daysToTrack):
        self.name = name
        self.daysToTrack = daysToTrack

        self.initMonth()

    def initMonth(self):
        today = datetime.today()
        year = today.year
        month = today.month
        key = f"{month}.{year}"

        lastDay = calendar.monthrange(year, month)[1]
        daysDict = {}

        for day in range(1, lastDay + 1):
            date = datetime(year, month, day)
            if date.weekday() in self.daysToTrack:
                daysDict[str(day)] = "none"

        # Load or initialize JSON data
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r") as f:
                try:
                    trackedData = json.load(f)
                except json.JSONDecodeError:
                    trackedData = {}
        else:
            trackedData = {}

        # Don't overwrite existing month
        if key in trackedData:
            print(f"Data for {key} already exists. No changes made.")
            return

        trackedData[key] = daysDict

        with open(FILE_NAME, "w") as f:
            json.dump(trackedData, f, indent=4)

        print(f"Added data for {key} to 'trackedData.json'.")

    def getData(self, month, year):
        monthYearString = f"{month}.{year}"
        if not os.path.exists(FILE_NAME):
            print(f"File '{FILE_NAME}' does not exist.")
            quit()

        with open(FILE_NAME, "r") as f:
            try:
                allMonthsData = json.load(f)
            except json.JSONDecodeError:
                print("File is not valid JSON.")
                quit()


        if monthYearString not in allMonthsData:
            print("Month not initialized yet!")
            quit()

        for monthYear in allMonthsData:
            if monthYear == monthYearString:
                return [[month, year], allMonthsData[monthYear]]

    def setData(self, onlyOneSet, month, year, day, value):
        day = str(day)
        month = str(month)
        year = str(year)

        monthYearString = f"{month}.{year}"
        if not os.path.exists(FILE_NAME):
            print(f"File '{FILE_NAME}' does not exist.")
            quit()

        with open(FILE_NAME, "r") as f:
            try:
                allMonthsData = json.load(f)
            except json.JSONDecodeError:
                print("File is not valid JSON.")
                quit()

        if monthYearString not in allMonthsData:
            print("Month or Year not found!")
            quit()

        currentMonthData = allMonthsData[monthYearString]

        if str(day) not in currentMonthData:
            print("Day not in days to track!")
            quit()

        if value not in ALLOWED_VALUES:
            print("Value not allowed!")
            quit()

        if onlyOneSet and currentMonthData[day] != "none":
            print("Value already set!")
            quit()


        allMonthsData[monthYearString][day] = value
        print(allMonthsData)

        with open(FILE_NAME, "w") as f:
            json.dump(allMonthsData, f, indent=4)

    def formatData(self, month, year):
        currentMonthData = self.getData(month, year)

        meta, dayData = currentMonthData
        metaMonth = int(meta[0])
        metaYear = int(meta[1])

        today = datetime.today()
        isCurrentMonth = (today.month == metaMonth and today.year == metaYear)
        currentDayStr = str(today.day)

        setAlready = "Set"
        if dayData[currentDayStr].lower() == "none":
            setAlready = "notSet"


        # Mapping values to colors
        colorMap = {
            "yes": Fore.GREEN + "YES" + Style.RESET_ALL,
            "no": Fore.RED + "NO" + Style.RESET_ALL,
            "none": Fore.WHITE + "NONE" + Style.RESET_ALL,
            "sick": Fore.BLUE + "SICK" + Style.RESET_ALL,
            "cancel": Fore.YELLOW + "CANCEL" + Style.RESET_ALL,
            "notSet": Fore.RED + "Value not set yet!" + Style.RESET_ALL,
            "Set": Fore.GREEN  + "Value set today!" + Style.RESET_ALL,
        }


        print(f"\n📅 Tracked Days for {meta[0]}/{meta[1]}")
        print(f"     {colorMap.get(setAlready)}")
        print(f"   {'Day':<4} |   Status")
        print("-" * 20)

        completedValues = {"yes", "cancel", "none"}
        completedCount = 0
        totalDays = len(dayData)

        for day in sorted(dayData.keys(), key=int):
            value = dayData[day].lower()
            status = colorMap.get(value, Fore.MAGENTA + value.upper() + Style.RESET_ALL)
            marker = "•" if isCurrentMonth and day == currentDayStr else " "
            print(f"{marker} {day:<5} | {status}")
            if value in completedValues:
                completedCount += 1



        percentage = (completedCount / totalDays) * 100 if totalDays > 0 else 0
        #print(f"\nCompletion: " + Fore.CYAN + f"{percentage:.1f}%" + Style.RESET_ALL + f"  ->  {completedCount} / {totalDays}")
        print(f"\nCompletion: {Fore.CYAN}{percentage:.1f}%{Style.RESET_ALL}  ->  {Fore.CYAN}{completedCount} / {totalDays}")


def run(mode, tracker, params: list = []):
    today = datetime.today()
    year = today.year
    month = today.month
    day = today.day


    match mode:
        case "show":
            tracker.formatData(month, year)
        case "set":
            tracker.setData(ALLOW_ONE_SET, month, year, day, params[0])


if __name__ == "__main__":
    tracker = Tracker(name="tracker", daysToTrack=[0, 1, 2, 3, 4, 5])
    #run("set", tracker, ["yes"])
    run("show", tracker)
