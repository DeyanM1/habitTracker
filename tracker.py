import calendar
import json
import os
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

ALLOWED_VALUES: list[str] = ["no", "yes", "sick", "cancel"]
DAYS_TO_TRACK : list[int] = [0, 1, 2, 3, 4, 5]
FILE_NAME     : str = "trackedData.json"
ALLOW_ONE_SET : bool = False
DEBUG         : bool = True
AUTO_CREATE_MONTH: bool = True



def initMonth(daysToTrack, customDayMonthYear = []):
    today = datetime.today()
    year: int = today.year
    month: int = today.month

    if len(customDayMonthYear) == 3:
        day = int(customDayMonthYear[0])
        month = int(customDayMonthYear[1])
        year = int(customDayMonthYear[2])

    key = f"{month}.{year}"

    lastDay = calendar.monthrange(year, month)[1]
    daysDict = {}

    for day in range(1, lastDay + 1):
        date = datetime(year, month, day)
        if date.weekday() in daysToTrack:
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

def getData(month: str, year: str) -> list:
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
    return []

def setData(onlyOneSet: bool, day: str, month: str, year: str,  value: str) -> None:
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

    with open(FILE_NAME, "w") as f:
        json.dump(allMonthsData, f, indent=4)

def formatData(month: str, year: str):
    currentMonthData = getData(month, year)

    meta, dayData = currentMonthData
    metaMonth: int = int(meta[0])
    metaYear: int = int(meta[1])

    today = datetime.today()
    isCurrentMonth = (today.month == metaMonth and today.year == metaYear)
    currentDayStr = str(today.day)

    setAlready = "notCurrentMonth"
    if isCurrentMonth:
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
        "notCurrentMonth": Fore.WHITE + "Not current Month!" + Style.RESET_ALL,
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

def sortData():
    if not os.path.exists(FILE_NAME):
        print("File 'trackedData.json' does not exist.")
        quit()

    try:
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Could not decode JSON from the file.")
        quit()

    if not isinstance(data, dict):
        print("Invalid format in JSON.")
        quit()

    # Helper: sort by year then month
    def sortKey(key):
        try:
            monthStr, yearStr = key.split(".")
            return (int(yearStr), int(monthStr))
        except ValueError:
            return (9999, 99)  # Put invalid keys last

    sortedKeys = sorted(data.keys(), key=sortKey)
    sortedData = {key: data[key] for key in sortedKeys}

    # Write sorted data back
    with open(FILE_NAME, "w") as f:
        json.dump(sortedData, f, indent=4)

    print("Sorted trackedData.json by month and year.")

def removeMonth(month, year):
    targetKey = f"{int(month)}.{int(year)}"

    if not os.path.exists(FILE_NAME):
        print("❌ File 'trackedData.json' does not exist.")
        return

    try:
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Could not decode JSON from the file.")
        return

    if targetKey not in data:
        print(f"⚠️ Month {targetKey} not found in trackedData.json.")
        return

    # Remove the key
    del data[targetKey]

    # Write updated data back
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Removed month {targetKey} from trackedData.json.")


def run(mode: str, customDayMonthYear: list[str] = [], otherParams: list[str] = []):
    today = datetime.today()
    year:  str = str(today.year)
    month: str = str(today.month)
    day:   str = str(today.day)

    if len(customDayMonthYear) > 0 and len(customDayMonthYear) == 3:
        if customDayMonthYear[0] != "":
            day = customDayMonthYear[0]

        if customDayMonthYear[1] != "":
            month = customDayMonthYear[1]

        if customDayMonthYear[2] != "":
            year = customDayMonthYear[2]


    match mode:
        case "show":
            formatData(month, year)
        case "set":
            setData(ALLOW_ONE_SET, day, month, year, otherParams[0]) # value
        case "sort":
            sortData()
        case "remove":
            removeMonth(month, year)
        case "init":
            newTracker = initMonth(DAYS_TO_TRACK, [day, month, year]) # month, year


if __name__ == "__main__":
    while True:
        run(input("Enter Mode -> "), customDayMonthYear=[input("-> "), input("-> "), input("-> ")], otherParams=[input("-> ")])
