import datetime


def serialize(obj: any):
    if isinstance(obj, (str, int, float)):
        return obj
    elif isinstance(obj, dict):
        return {serialize(key): serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple([serialize(item) for item in obj])
    elif hasattr(obj, "to_dict"):
        return serialize(obj.to_dict())
    return obj


def deserialize(obj: any):
    if isinstance(obj, (str, int, float)):
        return obj
    elif isinstance(obj, dict):
        return {deserialize(key): deserialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [deserialize(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple([deserialize(item) for item in obj])
    return obj


class Date:
    @classmethod
    def str_to_date(cls, date):
        if isinstance(date, list) or isinstance(date, tuple):
            return [
                datetime.datetime.strptime(single_date, "%Y-%m-%d")
                if isinstance(single_date, str)
                else single_date
                for single_date in date
            ]
        elif isinstance(date, str):
            return datetime.datetime.strptime(date, "%Y-%m-%d")
        else:
            raise TypeError("Date must be a list or str")

    @classmethod
    def date_to_str(cls, date):
        if isinstance(date, list) or isinstance(date, tuple):
            return [
                single_date.strftime("%Y-%m-%d")
                if isinstance(single_date, datetime.date)
                else single_date
                for single_date in date
            ]
        elif isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            return date.strftime("%Y-%m-%d")
        else:
            raise TypeError("Date must be list or datetime.datetime")

    @classmethod
    def today(cls) -> datetime.datetime:
        return datetime.datetime.now()

    @classmethod
    def prevdays(cls, timedelta: int = 1) -> datetime.datetime:
        return cls.today() - datetime.timedelta(days=timedelta)
