# flake8: noqa
from datetime import date, datetime
import pytest

from dateutil.tz import gettz

from yesaide.period import Day, Week, Month, PeriodError


EUROPE_PARIS = gettz("Europe/Paris")


def test_day():
    a_day = datetime(2017, 5, 4, tzinfo=EUROPE_PARIS)
    day_period = Day.from_reference_datetime(a_day)

    assert day_period.start() == datetime(2017, 5, 4, tzinfo=EUROPE_PARIS)
    assert day_period.end() == datetime(2017, 5, 5, tzinfo=EUROPE_PARIS)

    a_day_weird = datetime(2017, 5, 4, 20, tzinfo=gettz("America/Los_Angeles"))

    day_period = Day.from_reference_datetime(a_day_weird)

    assert day_period.first_day == date(2017, 5, 5)
    assert day_period.last_day == date(2017, 5, 5)

    day_period = Day.from_reference_datetime(a_day_weird, tzinfo=gettz("America/Los_Angeles"))

    assert day_period.first_day == date(2017, 5, 4)
    assert day_period.last_day == date(2017, 5, 4)

    a_day_naive = datetime(2017, 5, 4, 20)

    with pytest.raises(PeriodError):
        day_period = Day.from_reference_datetime(a_day_naive)


def test_week():
    a_day = date(2018, 2, 14)
    week_period = Week.from_reference_date(a_day)

    assert week_period.start() == datetime(2018, 2, 12, tzinfo=EUROPE_PARIS)
    assert week_period.end() == datetime(2018, 2, 19, tzinfo=EUROPE_PARIS)


def test_month():
    a_day = date(2018, 2, 23)
    month_period = Month.from_reference_date(a_day)

    assert month_period.start() == datetime(2018, 2, 1, tzinfo=EUROPE_PARIS)
    assert month_period.end() == datetime(2018, 3, 1, tzinfo=EUROPE_PARIS)
