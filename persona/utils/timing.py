from datetime import datetime, timedelta

def ms_to_time(ms):
    # Create a timedelta object with the provided milliseconds
    delta = timedelta(milliseconds=ms)

    # Create a datetime object with a base date (we'll extract the time part)
    base_date = datetime(1, 1, 1)

    # Add the timedelta to the base date to get the resulting datetime
    result_datetime = base_date + delta

    # Extract hours, minutes, and seconds from the resulting datetime
    days = result_datetime.day - 1
    hours = result_datetime.hour
    minutes = result_datetime.minute
    seconds = result_datetime.second

    # Format the result as DD:HH:MM:SS
    formatted_time = f"{days:02d} days, {hours:02d}:{minutes:02d}:{seconds:02d}"

    return formatted_time

# Example usage
if __name__ == "__main__":
    milliseconds = 1001 * 60 * 60 * 40 # Example milliseconds
    formatted_time = ms_to_time(milliseconds)
    print(formatted_time)