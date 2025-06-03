import calendar
from datetime import datetime
import os
import json
from colorama import Fore, Style, init
init(autoreset=True)

ALLOWED_VALUES: list[str] = ["no", "yes", "sick", "cancel", "break"]
TRACK_FILE_NAME = "trackedDataSimple.json"
DAYS_TO_TRACK = [0, 1, 2, 3, 4, 5]
ONE_PER_DAY = False
VERBOSE = False



def createFile() -> None:
    """Creates the initial File with Month; If file exists it only creates the month. Doesnt override DATA!
    """
    currentDate: datetime = datetime.today()

    currentDay: int = currentDate.day
    currentMonth: int = currentDate.month
    currentYear: int = currentDate.year

    currentDateKey: str = f"{currentMonth}.{currentYear}"

    lastDay = calendar.monthrange(currentYear, currentMonth)[1]
    daysDict = {}

    for day in range(1, lastDay + 1):
        date = datetime(currentYear, currentMonth, day)
        if date.weekday() in DAYS_TO_TRACK:
            daysDict[str(day)] = "none"

    # Load or initialize JSON data
    if os.path.exists(TRACK_FILE_NAME):
        with open(TRACK_FILE_NAME, "r") as f:
            try:
                trackedData = json.load(f)
            except json.JSONDecodeError:
                trackedData = {}
    else:
        trackedData = {}

    # Don't overwrite existing month
    if currentDateKey in trackedData:
        if VERBOSE:
            print(f"Data for {currentDateKey} already exists. No changes made.")
        return

    trackedData[currentDateKey] = daysDict

    with open(TRACK_FILE_NAME, "w") as f:
        json.dump(trackedData, f, indent=4)

    if VERBOSE:
        print(f"Added data for {currentDateKey} to '{TRACK_FILE_NAME}'.")

    sortData()

def setData(targetDateKey: str, value: str) -> None:
    """Set a value to a specified Day

    Args:
        targetDateKey (str): targetDateKey: (str): targetDate in format: MM.YYYY or t
        value (str): Value to set to specified day
    """
    currentDate: datetime = datetime.today()

    currentDay: int = currentDate.day
    currentMonth: int = currentDate.month
    currentYear: int = currentDate.year


    if targetDateKey == "t":
        targetDateKey = f"{currentMonth}.{currentYear}"


    if value not in ALLOWED_VALUES:
        print("Value not allowed!")
        return


    with open(TRACK_FILE_NAME, "r") as f:
        allMonthsData = json.load(f)

    if ONE_PER_DAY and targetDateKey == f"{currentMonth}.{currentYear}" and allMonthsData[targetDateKey] != "none":
        print("Only one set activated! Set already used!")
        return
    if str(currentDay) in allMonthsData[targetDateKey]:
        allMonthsData[targetDateKey][str(currentDay)] = value
    else:
        print("Value cant be set today, today is not a tracked day")
        return

    # allMonthsData[targetDateKey].update({str(currentDay): value})

    with open(TRACK_FILE_NAME, "w") as f:
        json.dump(allMonthsData, f, indent=4)

def getData(targetDateKey: str) -> list:
    """_summary_

    Args:
        targetDateKey: (str): targetDate in format: MM.YYYY

    Returns:
        list -> [[  int , int  ],    dict   ] \n
                [[ month, year ], monthData ]
    """
    month, year = targetDateKey.split(".")

    with open(TRACK_FILE_NAME, "r") as f:
        allMonthsData = json.load(f)


    if targetDateKey not in allMonthsData:
        if VERBOSE:
            print("Month not initialized yet!")
        quit()

    for monthYear in allMonthsData:
        if monthYear == targetDateKey:
            return [[month, year], allMonthsData[monthYear]]

    return []

def sortData() -> None:
    """Sorts the File
    """
    if not os.path.exists(TRACK_FILE_NAME):
        if VERBOSE:
            print(f"File '{TRACK_FILE_NAME}' does not exist.")
        quit()


    with open(TRACK_FILE_NAME, "r") as f:
        data = json.load(f)


    def sortKey(key):
        try:
            monthStr, yearStr = key.split(".")
            return (int(yearStr), int(monthStr))
        except ValueError:
            return (9999, 99)  # Put invalid keys last

    sortedKeys = sorted(data.keys(), key=sortKey)
    sortedData = {key: data[key] for key in sortedKeys}

    # Write sorted data back
    with open(TRACK_FILE_NAME, "w") as f:
        json.dump(sortedData, f, indent=4)

    if VERBOSE:
        print("Sorted trackedData.json by month and year.")

def formatData(targetDateKey: str) -> None:
    """_summary_

    Args:
        targetDateKey: (str): targetDate in format: MM.YYYY or t

    Returns:
        None
    """

    currentDate: datetime = datetime.today()
    currentDay: int = currentDate.day
    currentMonth: int = currentDate.month
    currentYear: int = currentDate.year



    if targetDateKey == "t":
        targetDateKey = f"{currentMonth}.{currentYear}"

    currentMonthData = getData(targetDateKey)

    meta, dayData = currentMonthData
    metaMonth: int = int(meta[0])
    metaYear: int = int(meta[1])


    isCurrentMonth = (currentMonth == metaMonth and currentYear == metaYear)

    setAlready = "notCurrentMonth"
    if isCurrentMonth:
        setAlready = "Set"
        try:
            if dayData[str(currentDay)].lower() == "none":
                setAlready = "notSet"
        except Exception as e:
            setAlready = "cantSet"


    # Mapping values to colors
    colorMap = {
        "yes": Fore.GREEN + "YES" + Style.RESET_ALL,
        "no": Fore.RED + "NO" + Style.RESET_ALL,
        "none": Fore.WHITE + "NONE" + Style.RESET_ALL,
        "sick": Fore.BLUE + "SICK" + Style.RESET_ALL,
        "cancel": Fore.YELLOW + "CANCEL" + Style.RESET_ALL,
        "break": Fore.YELLOW + "BREAK" + Style.RESET_ALL,
        "notSet": Fore.RED + "Value not set yet!" + Style.RESET_ALL,
        "Set": Fore.GREEN  + "Value set today!" + Style.RESET_ALL,
        "cantSet": Fore.YELLOW + "Value cant be set Today!" + Style.RESET_ALL,
        "notCurrentMonth": Fore.WHITE + "Not current Month!" + Style.RESET_ALL,
    }


    print(f"\n📅 Tracked Days for {meta[0]}/{meta[1]}")
    print(f"     {colorMap.get(setAlready)}")
    print(f"   {'Day':<4} |   Status")
    print("-" * 20)

    completedValuesFair = {"yes", "cancel", "none", "break"}
    completedCountFair = 0
    completedValuesUnFair = {"yes", "none"}
    completedCountUnFair = 0

    totalDays = len(dayData)

    for day in sorted(dayData.keys(), key=int):
        value = dayData[day].lower()
        status = colorMap.get(value, Fore.MAGENTA + value.upper() + Style.RESET_ALL)
        marker = "•" if isCurrentMonth and day == str(currentDay) else " "
        print(f"{marker} {day:<5} | {status}")
        if value in completedValuesFair:
            completedCountFair += 1
        if value in completedValuesUnFair:
            completedCountUnFair += 1




    percentageFair = (completedCountFair / totalDays) * 100 if totalDays > 0 else 0
    percentageUnFair = (completedCountUnFair / totalDays) * 100 if totalDays > 0 else 0
    #print(f"\nCompletion: " + Fore.CYAN + f"{percentage:.1f}%" + Style.RESET_ALL + f"  ->  {completedCount} / {totalDays}")
    print(f"\nCompletion Fair  : {Fore.CYAN}{percentageFair:.1f}%{Style.RESET_ALL}  ->  {Fore.CYAN}{completedCountFair} / {totalDays}")
    print(f"Completion Unfair: {Fore.CYAN}{percentageUnFair:.1f}%{Style.RESET_ALL}  ->  {Fore.CYAN}{completedCountUnFair} / {totalDays}")

def removeMonth(targetDateKey: str) -> None:
    """_summary_

    Args:
        targetDateKey: (str): targetDate in format: MM.YYYY or t

    Returns:
        None
    """
    currentDate: datetime = datetime.today()
    currentDay: int = currentDate.day
    currentMonth: int = currentDate.month
    currentYear: int = currentDate.year


    if targetDateKey == "t":
        targetDateKey = f"{currentMonth}.{currentYear}"


    with open(TRACK_FILE_NAME, "r") as f:
        data = json.load(f)


    if targetDateKey not in data:
        print(f"⚠️ {targetDateKey} not found in trackedData.json.")
        return

    del data[targetDateKey]

    with open(TRACK_FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

    if VERBOSE:
        print(f"✅ Removed month {targetDateKey} from trackedData.json.")

def selector(function: str):
    colorMap = {
        "y": Fore.GREEN + "Y" + Style.RESET_ALL,
        "n": Fore.RED + "n" + Style.RESET_ALL,
        "MM": Fore.RED + "MM" + Style.RESET_ALL,
        "YYYY": Fore.RED + "YYYY" + Style.RESET_ALL,
        "t": Fore.BLUE + "t" + Style.RESET_ALL,
        "today": Fore.BLUE + "today" + Style.RESET_ALL,

        "yes": Fore.GREEN + "YES" + Style.RESET_ALL,
        "no": Fore.RED + "NO" + Style.RESET_ALL,
        "none": Fore.WHITE + "NONE" + Style.RESET_ALL,
        "sick": Fore.BLUE + "SICK" + Style.RESET_ALL,
        "cancel": Fore.YELLOW + "CANCEL" + Style.RESET_ALL,
        "break": Fore.YELLOW + "BREAK" + Style.RESET_ALL,
        "notSet": Fore.RED + "Value not set yet!" + Style.RESET_ALL,
        "Set": Fore.GREEN  + "Value set today!" + Style.RESET_ALL,
        "notCurrentMonth": Fore.WHITE + "Not current Month!" + Style.RESET_ALL,
    }

    match function:
        case "set":
            print(f"Date format: '{colorMap.get("MM")}.{colorMap.get("YYYY")}' or '{colorMap.get("t")}' » {colorMap.get("today")}")
            targetDateKey = input("->> ")

            #print("Values: no | yes | sick | break | cancel")
            print(f"Values: {colorMap.get("no")} | {colorMap.get("yes")} | {colorMap.get("sick")} | {colorMap.get("break")} | {colorMap.get("cancel")}")
            value = input("->> ").lower()
            setData(targetDateKey, value)

        case "show":
            print(f"Date format: '{colorMap.get("MM")}.{colorMap.get("YYYY")}' or '{colorMap.get("t")}' » {colorMap.get("today")}")
            targetDateKey = input("->> ")
            formatData(targetDateKey)

        case "remove":
            print(f"Date format: '{colorMap.get("MM")}.{colorMap.get("YYYY")}' or '{colorMap.get("t")}' » {colorMap.get("today")}")
            targetDateKey = input("->> ")

            value = input(f"Are you sure? ({colorMap.get("y")}/{colorMap.get("n")}) -> ")
            if value.lower() == "y":
                quit()
            else:
                pass

            removeMonth(targetDateKey)

        case "exit":
            value = input(f"Exit? ({colorMap.get("y")}/{colorMap.get("n")}) -> ")
            if value.lower() == "y":
                quit()
            else:
                pass


if __name__ == "__main__":
    while True:
        print("---------------------------------------------------")
        createFile()
        print("Functions: set | show | remove | exit")
        selector(input("--> "))
