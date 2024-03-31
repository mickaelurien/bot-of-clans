from datetime import datetime, timezone

def getTimeLeft(str):
    date = datetime.strptime(str, "%Y%m%dT%H%M%S.%fZ")
    now = datetime.now()
    diff = date - now
    hours, left = divmod(diff.seconds, 3600)
    minutes, secondes = divmod(left, 60)

    return f"{f'{hours} heures,' if hours > 0 else ''} {minutes} minutes et {secondes} secondes"