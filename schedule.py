import MySQLdb
import os
import shutil
import subprocess

import dbconf


CSV_SEPARATOR = ","
CSV_FILE = 'schedule.csv'
TEX_SCHEDULE = 'schedule.tex'
TEX_OUTPUT = os.path.join('output', TEX_SCHEDULE)

db = MySQLdb.connect(
    host=dbconf.host,
    user=dbconf.username,
    passwd=dbconf.password,
    db=dbconf.db
)

cursor = db.cursor()
query_string = "SELECT contribution_title FROM `participant` "\
               "WHERE `first_name` LIKE '%s' "\
               "AND `last_name` LIKE '%s'"


class NotFoundException(Exception):
    pass


class Presentation(object):

    def __init__(self, presentation_time, first_name, last_name):
        self.presentation_time = presentation_time
        self.first_name = first_name
        self.last_name = last_name
        self.title = ''
        self._name = None

    @property
    def name(self):
        if self._name is None:
            self._name = "%s %s" % (self.first_name, self.last_name)
            return self._name
        return self._name

    def set_title(self, title):
        self.title = title

    def _replace_name(self, tex):
        return tex.replace(self.presentation_time, self.name)

    def _replace_title(self, tex):
        to_replace = "%s-TITLE" % self.presentation_time
        return tex.replace(to_replace, self.title)

    def replace_in_tex(self, tex):
        tex = self._replace_title(tex)
        return self._replace_name(tex)

    def __str__(self):
        return "%s - %s - %s" % (self.presentation_time, self.name, self.title)


def init_data():
    participants = []
    with open(CSV_FILE) as f:
        for line in f:
            time, first, last = line.strip().split(CSV_SEPARATOR)
            if not all([time, first, last]):
                continue
            participants.append(Presentation(time, first, last))
    for p in participants:
        cursor.execute(query_string % (p.first_name, p.last_name))
        row = cursor.fetchone()
        if row is None:
            msg = "Didn't find match for '%s %s'" % (p.first_name, p.last_name)
            raise NotFoundException(msg)
        p.set_title(row[0])
    return participants


def read_tex():
    with open(TEX_SCHEDULE) as f:
        return f.read()


def write_tex(tex):
    dirname = os.path.dirname(TEX_OUTPUT)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        shutil.copyfile('clifford.jpg', os.path.join(dirname, 'clifford.jpg'))
        shutil.copyfile('ut_logo.png', os.path.join(dirname, 'ut_logo.png'))
    with open(TEX_OUTPUT, 'w') as f:
        f.write(tex)


def compile_tex():
    output_dir = os.path.dirname(TEX_OUTPUT)
    proc = subprocess.Popen(
        ['pdflatex', '-output-director=%s' % output_dir, TEX_OUTPUT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    print stderr or stdout


def main():
    try:
        participants = init_data()
        for p in participants:
            print p
    except NotFoundException as e:
        print "ERROR OCCURED: %s" % e.message

    tex = read_tex()
    for p in participants:
        tex = p.replace_in_tex(tex)
    write_tex(tex)
    compile_tex()


if __name__ == '__main__':
    main()
