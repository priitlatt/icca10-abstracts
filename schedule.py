import os
import shutil
import subprocess


CSV_SEPARATOR = "\t"
CSV_FILE = 'schedule.tsv'
TEX_SCHEDULE = 'schedule.tex'
TEX_OUTPUT = os.path.join('output', TEX_SCHEDULE)


class Presentation(object):

    def __init__(self, presentation_time, first_name, last_name, title):
        self.presentation_time = presentation_time
        self.first_name = first_name
        self.last_name = last_name
        self.title = title

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

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


def unpack_line(line):
    splitted = line.strip().split(CSV_SEPARATOR)
    time, first, last, title = '', '', '', ''
    try:
        time = splitted[0]
        first = splitted[1]
        last = splitted[2]
        title = splitted[3]
    except IndexError:
        pass
    return (time, first, last, title)


def init_data():
    participants = []
    with open(CSV_FILE) as f:
        for line in f:
            if not line.strip("%s\n\t " % CSV_SEPARATOR):
                continue
            data = unpack_line(line)
            if not all(data):
                print "Warnig, something is missing: %s" % str(data)
            participants.append(Presentation(*data))
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
    cmd = ['pdflatex', '-output-director=%s' % output_dir, TEX_OUTPUT]
    print "executing '%s'" % ' '.join(cmd)
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print stderr or stdout


def main():
    participants = init_data()
    for p in participants:
        print p

    tex = read_tex()
    for p in participants:
        tex = p.replace_in_tex(tex)
    write_tex(tex)
    compile_tex()


if __name__ == '__main__':
    main()
