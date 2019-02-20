"""An attempt at making a period abstraction which does not suck.
Notably, a period abstraction which plays nice with timezones.

"""
from abc import ABCMeta, abstractmethod
from datetime import date, datetime, timedelta, time
from typing import Any, Iterator

from dateutil.tz import gettz


EUROPE_PARIS = gettz("Europe/Paris")


def _at_midnight(a_date: date, tzinfo=gettz("Europe/Paris")) -> datetime:
    return datetime.combine(a_date, time(hour=0, minute=0, tzinfo=tzinfo))


class PeriodError(Exception):
    """Base class for period exceptions."""


def raise_if_not_date(candidate: Any) -> None:
    """Raise an exception if the given value is not strictly a date."""
    # That looks weird, Pythonic way would be to use `isinstance`, but
    # as `date` inherits from `datetime`, a `datetime` would pass the
    # test (and we do not want datetimes here).
    if type(candidate) != date:
        raise PeriodError("Given value is not strictly a date")


def raise_if_not_datetime_ta(candidate: Any) -> None:
    """Raise an exception if the given value is not a timezone aware
    datetime.

    """
    if not isinstance(candidate, datetime):
        raise PeriodError("Given value is not strictly a datetime")

    if candidate.tzinfo is None:
        raise PeriodError('Given datetime is "naive" (no timezone is attached to it)')


class Period(metaclass=ABCMeta):
    def __init__(self, *, first_day, last_day):
        raise_if_not_date(first_day)
        raise_if_not_date(last_day)
        self.first_day = first_day
        self.last_day = last_day

    @classmethod
    def from_reference_datetime(cls, reference_datetime, *, tzinfo=EUROPE_PARIS) -> "Period":
        """Return the period containing the given datetime in the given
        timezone.

        This one is a bit hairy, but for instance, "monday at 3am in
        Europe/Paris" and "sunday at 11pm America/Somewhere" is the same
        datetime, hence to determine the period we need to know in which
        timezone we want to "see" this datetime.

        """
        raise_if_not_datetime_ta(reference_datetime)
        reference_date = reference_datetime.astimezone(tz=tzinfo).date()
        return cls.from_reference_date(reference_date)

    @staticmethod
    @abstractmethod
    def from_reference_date(reference_date: date) -> "Period":
        pass

    def start(self, *, tzinfo=EUROPE_PARIS) -> datetime:
        """Return the first instant of the period in the given timezone
        (a timezone aware datetime).

        """
        return _at_midnight(self.first_day, tzinfo=tzinfo)

    def end(self, *, tzinfo=EUROPE_PARIS) -> datetime:
        """Return the last instant of the period in the given timezone
        (a timezone aware datetime).

        """
        return self.next().start(tzinfo=tzinfo)

    @classmethod
    def current(cls, *, tzinfo=EUROPE_PARIS) -> "Period":
        """Return the period containing the date of "today" in the
        given timezone.

        """
        return cls.from_reference_date(datetime.now(tzinfo).date())

    def next(self) -> "Period":
        """Return the period directly following the current period.

        The trick is to add 1 day to the last day of the period to land
        in the next period, and use this date as the `reference_date`
        for the next period.

        """
        return type(self).from_reference_date(self.last_day + timedelta(days=1))

    def previous(self) -> "Period":
        """Return the period directly preceding the current period."""
        # See `Period.next()` docstring for an explanation.
        return type(self).from_reference_date(self.first_day - timedelta(days=1))

    @classmethod
    def iter_between_datetime(
        cls, *, from_datetime: datetime, to_datetime: datetime, tzinfo=EUROPE_PARIS
    ) -> Iterator["Period"]:
        """Return an iterator yielding all periods between (and
        including) the two given datetimes in the given timezone.

        """
        raise_if_not_datetime_ta(from_datetime)
        raise_if_not_datetime_ta(to_datetime)
        from_date = from_datetime.astimezone(tz=tzinfo).date()
        to_date = to_datetime.astimezone(tz=tzinfo).date()
        yield from cls.iter_between_date(from_date=from_date, to_date=to_date)

    @classmethod
    def iter_between_date(cls, *, from_date: date, to_date: date) -> Iterator["Period"]:
        """Return an iterator yielding all periods between (and
        including) the two given dates.

        """
        raise_if_not_date(from_date)
        raise_if_not_date(to_date)
        current_period = cls.from_reference_date(from_date)
        yield current_period

        while True:
            next_period = current_period.next()

            # Iteration is over
            if next_period.first_day > to_date:
                break

            yield next_period
            current_period = next_period


class Day(Period):
    @staticmethod
    def from_reference_date(reference_date: date) -> "Day":
        raise_if_not_date(reference_date)
        return Day(first_day=reference_date, last_day=reference_date)


class Week(Period):
    @staticmethod
    def from_reference_date(reference_date: date) -> "Week":
        raise_if_not_date(reference_date)
        first_day_label = reference_date.strftime("%G%V1")
        last_day_label = reference_date.strftime("%G%V7")
        return Week(
            first_day=datetime.strptime(first_day_label, "%G%V%u").date(),
            last_day=datetime.strptime(last_day_label, "%G%V%u").date(),
        )


class Month(Period):
    @staticmethod
    def from_reference_date(reference_date: date) -> "Month":
        raise_if_not_date(reference_date)
        first_day = date(reference_date.year, reference_date.month, 1)
        first_day_next_month = (first_day + timedelta(days=31)).replace(day=1)
        last_day = first_day_next_month - timedelta(days=1)
        return Month(first_day=first_day, last_day=last_day)


_PERIOD_TYPE_TO_PERIOD = {"daily": Day, "weekly": Week, "monthly": Month}


def period_from_string(period_string):
    return _PERIOD_TYPE_TO_PERIOD[period_string]
