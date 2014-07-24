import MySQLdb

import dbconf

VALID_SESSIONS = [
    'talkPlenary', 'talk', 'talkPhysics', 'talkAnalysis',
    'talkStandardModel', 'talkGACurriculum', 'talkFourierAndWavelets',
    'talkFromSignalsToConsciousness', 'talkConformal'
]

SEPARATOR = ','

FIRST_NAME = 0
LAST_NAME = 1
SESSION = 2
TITLE = 8
ABSTRACT = 10


db = MySQLdb.connect(
    host=dbconf.host,
    user=dbconf.username,
    passwd=dbconf.password,
    db=dbconf.db
)

cursor = db.cursor()
query_string = "SELECT first_name, last_name, contribution_title, "\
               "contribution_abstract FROM `participant` "\
               "WHERE `first_name` LIKE '%s' AND `last_name` LIKE '%s'"


class NotFoundException(Exception):
    pass


class Participant(object):

    def __init__(self, row):
        self._first, self._last, session = row.strip().split(SEPARATOR)
        self.session = session
        cursor.execute(query_string % (
            self._first.strip(), self._last.strip()))
        result = cursor.fetchone()

        if result is None:
            self.first_name, self.last_name = '', ''
            self.title, self.abstract = '', ''
            return
        self.first_name = result[0].title()
        self.last_name = result[1].title()
        self.title = result[2]
        self.abstract = result[3]

    def is_valid(self):
        fields = (
            self.first_name, self.last_name, self.title,
            self.abstract, self.session in VALID_SESSIONS
        )
        if all(fields):
            # print "Valid participant: '%s %s'" % (self._first, self._last)
            return True
        if self.session in VALID_SESSIONS:
            print "Invalid participant: '%s %s'" % (self._first, self._last)

    def get_abstract_tex(self):
        abstract = self.abstract.replace('\n', ' ')
        args = (self.first_name, self.last_name, self.title, abstract)
        return "\\abstract{%s}{%s}{%s}{%s}\n" % args

    def get_order_key(self):
        return "%s %s" % (self.last_name, self.first_name)


def get_participants():
    participants = []
    with open('abstracts.csv') as f:
        for row in f:
            participants.append(Participant(row))
    return sorted(participants, key=lambda p: p.get_order_key())


def generate_tex(participants):
    for p in participants:
        if p.is_valid():
            print p.get_tex()


def save_abstracts(abstracts):
    with open('_abstracts_', 'w') as f:
        f.writelines(abstracts)


def main():
    abstracts = []
    participants = get_participants()
    for p in participants:
        if p.is_valid():
            abstracts.append(p.get_abstract_tex())
    save_abstracts(abstracts)


if __name__ == '__main__':
    main()
