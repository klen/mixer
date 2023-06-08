from faker.providers import BaseProvider

from .constants import GENRES, TEAMS


class Provider(BaseProvider):
    def title(self):
        words = self.generator.words(self.generator.random_int(2, 5))
        return " ".join(words).title()

    def genre(self):
        return self.random_element(GENRES)

    def team(self):
        return self.random_element(TEAMS)
