#!/usr/bin/env python
from glob import glob
from mako.template import Template
from mako.lookup import TemplateLookup
from sys import argv
from os import unlink, mkdir, listdir, chdir, getcwd
from os.path import join, isdir, split
from shutil import copytree, rmtree
from subprocess import Popen, PIPE
from yaml import load
from operator import itemgetter

def clean():
    if isdir("build/js"):
        rmtree("build/js")

    for f in glob("build/*.html"): unlink(f)

def build():
    if not isdir("build"):
        mkdir("build")

    def required(page, required_vars):
        for var in required_vars: page[var] = page.get(var, "")

    chapters = [load(file(c)) for c in glob("chapters/*.yaml")]

    pages = []
    toc = []
    for chapter in sorted(chapters, key=itemgetter('order')):
        link = "%s.html" % chapter["name"]
        chapter["outfilename"] = join("build", link)

        pages.append(chapter)
        toc.append((chapter["title"], link))

        required(chapter, ["code", "explain_before", "explain_after", "title", "hidden_code",
                           "library"])

    for i, page in enumerate(pages):
        page["prev"] = pages[i-1]["name"] if i > 0 else ""
        page["next"] = pages[i+1]["name"] if i+1 < len(pages) else ""
        page["toc"]  = toc
        file(page["outfilename"], 'w').write(
             Template(filename="templates/template.mak", input_encoding='utf-8',
                      lookup=TemplateLookup(directories=['.'])).render(**page).encode('utf-8'))

    copytree("js", "build/js")

def deploy():
    print "deploying"
    for f in ['build/*.html', 'js']:
        cmd = "rsync -avuz -e ssh %s llimllib@billmill.org:~/static/canvastutorial" % f
        p = Popen(cmd, shell=True, stderr=PIPE)

if __name__ == "__main__":
    clean()
    build()
    if argv[-1].lower() == "deploy":
        deploy()
