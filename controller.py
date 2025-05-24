import argparse
import tracker

def main():
    parser = argparse.ArgumentParser(description="Track your Data with HABIT-TRACK")

    #subparsers = parser.add_subparsers(dest="function", required=True, help="Choose a function to run")

    parser.add_argument("function", help="Show the data from the the saved File")
    parser.add_argument("-d", "--day", type = str, default="", help="Set the day to show the values")
    parser.add_argument("-m", "--month", type = str, default="", help="Set the month to show the values")
    parser.add_argument("-y", "--year", type = str, default="", help="Set the year to show the values")


    args = parser.parse_args()

    easyArgs = ["show", "sort", "remove", "init"]
    if args.function in easyArgs:
        tracker.run(args.function, customDayMonthYear=[args.day, args.month, args.year])









if __name__ == "__main__":
    main()
