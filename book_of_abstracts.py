import MySQLdb
import os
import shutil
import subprocess

import dbconf

CSV_SEPARATOR = "\t"
CSV_FILE = 'ettekanded.tsv'
TEX_ABSTRACTS = 'book_of_abstracts.tex'
TEX_OUTPUT = os.path.join('output', TEX_ABSTRACTS)

VALID_SESSIONS = [
    'talkPlenary', 'talk', 'talkPhysics', 'talkAnalysis',
    'talkStandardModel', 'talkGACurriculum', 'talkFourierAndWavelets',
    'talkFromSignalsToConsciousness', 'talkConformal'
]

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

    def __init__(self, splitted_row):
        self._first, self._last, session = splitted_row[:3]
        self.session = session
        cursor.execute(query_string % (
            self._first.strip(), self._last.strip()))
        result = cursor.fetchone()

        if result is None:
            self.first_name, self.last_name = '', ''
            self.title, self.abstract = '', ''
            print "%s %s not found from db" % (self._first, self._last)
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
            return True
        if self.session in VALID_SESSIONS:
            print "Invalid participant: '%s %s'" % (self._first, self._last)

    def get_abstract_tex(self):
        abstract = self.abstract.replace('\n', ' ')
        name = "%s %s" % (self.first_name, self.last_name)
        args = (name, self.first_name, self.last_name, self.title, abstract)
        return "%% %s\n\\abstract{%s}{%s}{%s}{%s}\n\n" % args

    def get_order_key(self):
        return "%s %s" % (self.last_name, self.first_name)


def get_participants():
    participants = []
    with open(CSV_FILE) as f:
        next(f)  # skip headers
        for row in f:
            splitted = row.strip().split(CSV_SEPARATOR)[:3]
            if not row.strip() or len(splitted) < 3:
                continue
            participants.append(Participant(splitted))
    return sorted(participants, key=lambda p: p.get_order_key())


def generate_abstracts(participants):
    s = ""
    for p in participants:
        if p.is_valid():
            s += p.get_abstract_tex()
    return s


def read_tex():
    with open(TEX_ABSTRACTS) as f:
        return f.read()


def write_tex(tex):
    dirname = os.path.dirname(TEX_OUTPUT)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        shutil.copyfile('clifford_large.jpg',
                        os.path.join(dirname, 'clifford_large.jpg'))
    with open(TEX_OUTPUT, 'w') as f:
        f.write(tex)


def compile_tex():
    output_dir = os.path.dirname(TEX_OUTPUT)
    cmd = ['pdflatex', '-output-director=%s' % output_dir, TEX_OUTPUT]
    print "executing '%s'" % ' '.join(cmd)
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate('X')
    print stderr or stdout
    if proc.returncode != 0:
        print "\n\nCOMPILING TEX FAILED see log for more information."


def main():
    raw = read_tex()
    participants = filter(lambda p: p.is_valid(), get_participants())
    abstracts_tex = generate_abstracts(participants)
    write_tex(raw.replace('ABSTRACTS-LOCATION', abstracts_tex))
    compile_tex()


if __name__ == '__main__':
    main()
