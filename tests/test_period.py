# flake8: noqa
from datetime import date, datetime, timedelta
import pytest

from dateutil.tz import gettz

from yesaide.period import Day, Week, Month, PeriodError


EUROPE_PARIS = gettz("Europe/Paris")


def test_day():
    a_day = date(2017, 5, 4)
    day_period = Day.from_reference_date(a_day)

    assert day_period.first_day == a_day
    assert day_period.last_day == a_day

    for i, d in enumerate(
        Day.iter_between_date(from_date=a_day, to_date=a_day + timedelta(days=10))
    ):
        assert d.first_day == a_day + timedelta(days=i)
        assert d.last_day == a_day + timedelta(days=i)

    a_datetime = datetime(2017, 5, 4, 20)

    with pytest.raises(PeriodError):
        day_period = Day.from_reference_date(a_datetime)

    current_day = Day.current()
    assert current_day.first_day == datetime.now(EUROPE_PARIS).date()
    assert current_day.last_day == datetime.now(EUROPE_PARIS).date()

    next_day = current_day.next()
    assert next_day.first_day == datetime.now(EUROPE_PARIS).date() + timedelta(days=1)
    assert next_day.last_day == datetime.now(EUROPE_PARIS).date() + timedelta(days=1)

    previous_day = current_day.previous()
    assert previous_day.first_day == datetime.now(EUROPE_PARIS).date() - timedelta(days=1)
    assert previous_day.last_day == datetime.now(EUROPE_PARIS).date() - timedelta(days=1)


def test_week():
    a_day = date(2018, 2, 14)
    week_period = Week.from_reference_date(a_day)

    assert week_period.first_day == date(2018, 2, 12)
    assert week_period.last_day == date(2018, 2, 18)

    weeks_theory = [
        (date(2018, 2, 12), date(2018, 2, 18)),
        (date(2018, 2, 19), date(2018, 2, 25)),
        (date(2018, 2, 26), date(2018, 3, 4)),
        (date(2018, 3, 5), date(2018, 3, 11)),
        (date(2018, 3, 12), date(2018, 3, 18)),
        (date(2018, 3, 19), date(2018, 3, 25)),
    ]

    weeks_output = list(Week.iter_between_date(from_date=a_day, to_date=date(2018, 3, 24)))

    assert len(weeks_output) == len(weeks_theory)

    for w_theory, w_output in zip(weeks_theory, weeks_output):
        assert w_output.first_day == w_theory[0]
        assert w_output.last_day == w_theory[1]

    current_week = Week.current()
    assert current_week.first_day <= datetime.now(EUROPE_PARIS).date()
    assert current_week.last_day >= datetime.now(EUROPE_PARIS).date()


def test_month():
    a_day = date(2018, 2, 23)
    month_period = Month.from_reference_date(a_day)

    assert month_period.first_day == date(2018, 2, 1)
    assert month_period.last_day == date(2018, 2, 28)

    months_theory = [
        (date(2018, 2, 1), date(2018, 2, 28)),
        (date(2018, 3, 1), date(2018, 3, 31)),
        (date(2018, 4, 1), date(2018, 4, 30)),
        (date(2018, 5, 1), date(2018, 5, 31)),
    ]

    months_output = list(Month.iter_between_date(from_date=a_day, to_date=date(2018, 5, 17)))

    assert len(months_output) == len(months_theory)

    for w_theory, w_output in zip(months_theory, months_output):
        assert w_output.first_day == w_theory[0]
        assert w_output.last_day == w_theory[1]

    current_month = Month.current()
    assert current_month.first_day <= datetime.now(EUROPE_PARIS).date()
    assert current_month.last_day >= datetime.now(EUROPE_PARIS).date()
