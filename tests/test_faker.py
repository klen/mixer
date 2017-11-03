def test_faker():
    from mixer._faker import faker

    assert faker.choices()
    assert len(faker.choices(length=5)) == 5

    assert faker.big_integer()
    assert faker.ip_generic()

    assert faker.positive_decimal()
    assert faker.positive_decimal() > 0

    assert faker.positive_integer()
    assert faker.positive_integer() > 0

    assert faker.small_integer()

    assert faker.small_positive_integer()
    assert faker.small_positive_integer() > 0
    assert faker.small_positive_integer() <= 32767

    assert faker.uuid()

    assert 0 <= faker.percent() <= 100

    assert faker.percent_decimal()
    assert faker.title()
    assert faker.coordinates()

    env = faker.env

    name = faker.name
    faker.locale = 'ru'

    assert name()
    assert faker.name()

    faker.locale = 'en'
    assert faker.name()
    assert faker.env is env

    assert faker.email()

    assert faker.pybytes()

    assert faker.date_time_this_month()
