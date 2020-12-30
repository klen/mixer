def test_faker():
    from mixer._faker import faker

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
    assert faker.day_of_week() in {
        "Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"}

    assert name()
    assert faker.name()

    faker.locale = 'en'
    assert faker.day_of_week() in {
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}

    assert faker.name()
    assert faker.env is env

    assert faker.email()

    assert faker.pybytes()

    assert faker.date_time_this_month()
