#!python3

import os
import sys
import json
import inspect
import pathlib
import subprocess

from typing import Dict, List
from datetime import datetime

VERBOSITY = int(sys.argv[1]) if len(sys.argv) > 1 else 0

TARGET    = "docs"
TEMPLATES = "templates"
PREFIX    = os.path.dirname(__file__)

def cleanup():
    for f in [f'{TARGET}/index.html', f'{TARGET}/news.html', f'{TARGET}/pubs.html', f'{TARGET}/main.css']:
        try:
            os.remove(f)
        except Exception as _:
            pass

# for printing with colours
class bcolors:
    SUCCESS = '\033[92m'
    OKCYAN  = '\033[96m'
    OKBLUE  = '\033[94m'
    WARNING = '\033[93m'
    ERROR   = '\033[91m'
    BOLD    = '\033[1m'
    ENDC    = '\033[0m'

# Helper functions
def status(msg: str, priority = 1):
    if priority <= VERBOSITY:
        if priority == 0:
            divider = "*"*len(msg)
            msg     = f"{divider}\n{msg}\n{divider}"
            print(f"{bcolors.BOLD}{bcolors.OKBLUE}{msg}{bcolors.ENDC*2}")
        elif priority == 1:
            print(f"{bcolors.BOLD}{bcolors.OKCYAN}{msg}{bcolors.ENDC*2}")
        else:
            print(f"{bcolors.OKCYAN}{msg}{bcolors.ENDC}")

def success(msg: str):
    msg     = f"SUCCESS: {msg}"
    divider = "*"*len(msg)
    msg     = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.SUCCESS}{msg}{bcolors.ENDC}")

def warning(msg: str):
    msg     = f"WARNING: {msg}"
    divider = "*"*len(msg)
    msg     = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")

def error(msg: str):
    msg     = f"ERROR: {msg}"
    divider = "*"*len(msg)
    msg     = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.ERROR}{msg}{bcolors.ENDC}")
    cleanup()
    exit(1)

def warn_if_not(cond: bool, msg: str):
    if not cond:
        warning(msg)

def fail_if_not(cond: bool, msg: str):
    if not cond:
        error(msg)

def fill_if_missing(json: Dict[str, str], field: str, default = ""):
    if not field in json:
        json[field] = default

    return json

def is_federicos():
    try:
        repo_url = subprocess.getoutput(f"git -C {PREFIX} config --get remote.origin.url").split()[0]
    except Exception as _:
        repo_url = ""

    federicos_url   = "git@github.com:FedericoAureliano/FedericoAureliano.github.io.git"
    name            = meta_json["name"]
    federicos_name  = "Federico Mora Rocha"
    
    return name == federicos_name and repo_url == federicos_url

def check_tracker():
    status("- Sanity check on tracker script")

    tracker = meta_json["tracker"]

    not_mine_implies_not_my_tracker = is_federicos() or "federicoaureliano" not in tracker
    fail_if_not(not_mine_implies_not_my_tracker, "Please use your own tracker in data/meta.json")

def check_cname():
    status("- Sanity check on CNAME")

    path = os.path.join(PREFIX, "docs", "CNAME")
    try:
        with open(path) as f:
            cname = f.read()
    except Exception as _:
        status(f"  - Couldn't load CNAME---treating it as empty.", 1)
        cname = ""

    not_mine_implies_not_my_cname = is_federicos() or "federico.morarocha.ca" != cname
    fail_if_not(not_mine_implies_not_my_cname, f"Please use your own CNAME at {path}")


def read_data(json_file_name: str, optional: bool):
    path = os.path.join(PREFIX, json_file_name)
    try:
        with open(path) as f:
            status(f"- loading {path}")
            data = json.load(f)
    except Exception as _:
        fail_if_not(optional, f"Failed to parse {path}. Check your commas, braces, and if the file exists.")
        # fail_if_not will exit if needed so the code below will only run if this data is optional
        status(f"Failed to load {path}---treating it as empty.", 0)
        data = {}
    
    return data

def read_template(template_file_name: str, optional: bool):
    path = os.path.join(PREFIX, template_file_name)
    with open(path) as f:
        status(f"- loading {path}")
        try:
            data = f.read()
        except Exception as _:
            fail_if_not(optional, f"Failed to read {path}. Does it exist?")
            # fail_if_not will exit if needed
            status(f"Couldn't load {path}---treating it as empty.", 0)
            data = ""
    
    return data

def write_file(file_name: str, contents: str):
    path = os.path.join(PREFIX, file_name)
    if contents == "":
        return

    with open(path, 'w') as target:
        status(f"- writing {path}")
        target.write(contents)

def replace_placeholders(text: str, map: Dict[str, str]):
    newtext = text

    for k in map:
        newtext = newtext.replace(k+"-placeholder", map[k])

    return newtext

# Define functions for website pieces
def build_news(news: List[Dict[str, str]], count: int, standalone: bool):
    if count > len(news):
        count = len(news)

    if count <= 0:
        return ""
    
    status("\nAdding news:")
    news_list = ""

    for n in news[:count]:
        status("- " + n["date"])
        item  = '<div class="news-item">\n'
        item += '<div class="news-left">'  + n["date"] + '</div>\n'
        item += '<div class="news-right">' + n["text"] + '</div>\n'
        item += '</div>\n'
        news_list += item

    news_html = "<div class=\"section\">\n"

    if (count != len(news)):
        link       = "<a href=\"./news.html\">See all posts</a>"
        news_html += "<h1>Recent News <small style=\"font-weight: 300; float: right; padding-top: 0.23em\">(%s)</small></h1>\n" %link
    elif standalone:
        link       = "<a href=\"./index.html\">%s</a>" % meta_json["name"]
        news_html += "<h1>News <small style=\"font-weight: 300; float: right; padding-top: 0.23em\">%s</small></h1>\n" %link
    else:
        news_html += "<h1>News</h1>\n"

    news_html += "<div class=\"hbar\"></div>\n"
    news_html += "<div id=\"news\">\n"
    news_html += news_list
    news_html += "</div>\n" # close news
    news_html += "</div>\n" # close section

    return news_html

# Helper function to decide what publication sections to include
def get_pub_titles(pubs: List[Dict[str, str]]):
    titles = set()
    for p in pubs:
        titles.add(p["section"])

    return sorted(list(titles))

def some_not_selected(pubs: List[Dict[str, str]]):
    for p in pubs:
        if not p["selected"]:
            return True

    return False

def build_pubs_inner(pubs: List[Dict[str, str]], title: str, full: bool):
    if title == "":
        return ""

    pubs_list = ""

    for p in pubs:
        if title == p["section"] and (p["selected"] or full):
            status("- " + p["title"])
            item  = '<div class="paper">\n'
            item += '<div class="paper-flex">\n'
            item += '<div class="paper-conference">' + p["conference"] + '</div>\n'
            item += '<div class="paper-details">\n'
            item += '<div class="paper-title">' + p["title"] + '</div>\n'
            item += '<div class="paper-authors">' + ",\n".join(p["authors"].split(", ")) + '</div>\n'
            item += '</div>\n' # close paper-details
            item += '<div class="paper-icons">\n'
            item += '<a href="' + p["link"] + '" alt="[PDF] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>' % (style_json["paper-img"], style_json["paper-img-dark"]) if p["link"] else ""
            item += '<a href="' + p["extra"] + '" alt="[Extra] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>' % (style_json["extra-img"], style_json["extra-img-dark"]) if p["extra"] else ""
            item += '<a href="' + p["slides"] + '" alt="[Slides] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>' % (style_json["slides-img"], style_json["slides-img-dark"]) if p["slides"] else ""
            item += '</div>\n' # close paper-icons
            item += '</div>\n' # close paper-flex
            item += '</div>\n' # close paper
            pubs_list += item

    pubs_html  = "<h3 id=\"%spublications\">%s</h3>" % (title, title)
    pubs_html += pubs_list

    return pubs_html

def build_pubs(pubs: List[Dict[str, str]], full: bool):
    if len(pubs) == 0:
        return ""

    status("\nAdding publications:")

    pubs_html =  "<div class=\"section\">\n"

    if some_not_selected(pubs) and not full: 
        pubs_html += "<h1>Selected Publications <small style=\"font-weight: 300; float: right; padding-top: 0.23em\">(<a href=\"./pubs.html\">See all publications</a>)</small></h1>" 
    elif full: 
        link       = "<a href=\"./index.html\">%s</a>" % meta_json["name"]
        pubs_html += "<h1>Publications <small style=\"font-weight: 300; float: right; padding-top: 0.23em\">%s</small></h1>\n" %link
    else: 
        pubs_html += "<h1>Publications</h1>"

    pubs_html += "<div class=\"hbar\"></div>\n"
    pubs_html += "<div id=\"publications\">\n"

    titles = get_pub_titles(pubs)

    for i in range(len(titles)):
        title      = titles[i]
        pubs_html += build_pubs_inner(pubs, title, full)

    pubs_html += "</div>\n" # close pubs
    pubs_html += "</div>\n" # close section

    return pubs_html

def build_students(students: List[Dict[str, str]]):
    if len(students) == 0:
        return ""

    status("\nAdding students:")
    students_list = ""

    for p in students:
        status("- " + p["name"])
        item  = '<div class="student">\n' + p["name"] + "\n"
        item += '<div class="student-project">' + p["project"] + '</div>\n'
        item += '<div class="student-result">' + p["result"] + '</div>\n'
        item += '</div>\n'
        students_list += item

    students_html  = "<div class=\"section\">\n"
    students_html += "<h1>Mentoring</h1>\n"
    students_html += "<div class=\"hbar\"></div>\n"
    students_html += "<div id=\"students\">\n"
    students_html += students_list
    students_html += "</div>\n" # close students
    students_html += "</div>\n" # close section

    return students_html

def build_profile(profile: Dict[str, str]):
    profile_html  = "<div class=\"profile\">\n"
    profile_html += "<img class=\"headshot\" src=\"%s\" alt=\"Headshot\"/>\n" % profile["headshot"]
    profile_html += profile["blurb"]
    profile_html += "\n<p>Here is my "
    profile_html += "<a href=\"%s\">CV</a> and " % profile["cv"]
    profile_html += "<a href=\"%s\">Google Scholar</a>. " % profile["scholar"]
    profile_html += "You can reach me at %s." % profile["email"]
    profile_html += "</p>\n" # close description paragraph
    profile_html += "</div>\n" # close profile

    return profile_html

def add_links(html: str, links: Dict[str, str]):
    status("\nAdding links:", 2)

    toreplace = sorted(links.keys(), key=len, reverse=True)

    for name in toreplace:
        pos = html.find(name)
        while pos != -1:
            prefix = html[:pos]
            suffix = html[pos:]

            open  = html[:pos].count("<a href=")
            close = html[:pos].count("</a>")

            status(f"- {name} {pos} {open} {close}", 2)
            target = name + " "
            if pos >= 0 and open == close:
                target = "<a href=\"%s\">%s</a>" % (links[name], name)
                suffix = suffix.replace(name, target, 1)
                html   = prefix+suffix

            start = (len(prefix) - len(name)) + len(target) # we got rid of name and replaced it with target
            tmp   = html[start:].find(name)
            pos   = tmp + start if tmp >= 0 else tmp
    
    return html

def build_index(profile_json: Dict[str, str], news_json: List[Dict[str, str]], pubs_json: List[Dict[str, str]], students_json: List[Dict[str, str]], links: Dict[str, str]):
    body_html  = "<body>\n"
    body_html += "<header><div id=\"scroller\"></div></header>\n"
    body_html += "<div class=\"content\">\n"
    body_html += build_profile(profile_json)
    body_html += build_news(news_json, 5, False)
    body_html += build_pubs(pubs_json, False)
    body_html += build_students(students_json)
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    index_page  = "<!DOCTYPE html>\n"
    index_page += "<html lang=\"en\">\n"
    index_page += head_html + "\n\n"
    index_page += body_html
    index_page += "</html>\n"

    return inspect.cleandoc(add_links(index_page, links))

def build_news_page(news_json: List[Dict[str, str]], links: Dict[str, str]):
    content = build_news(news_json, len(news_json), True)

    if content == "":
        return ""

    body_html  = "<body>\n"
    body_html += "<header><div id=\"scroller\"></div></header>\n"
    body_html += "<div class=\"content\">\n"
    body_html += content
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    news_html  = "<!DOCTYPE html>\n"
    news_html += "<html lang=\"en\">\n"
    news_html += head_html + "\n\n"
    news_html += body_html
    news_html += "</html>\n"

    return inspect.cleandoc(add_links(news_html, links))

def build_pubs_page(pubs_json: List[Dict[str, str]], links: Dict[str, str]):
    content = build_pubs(pubs_json, True)

    if content == "":
        return ""

    body_html  = "<body>\n"
    body_html += "<header><div id=\"scroller\"></div></header>\n"
    body_html += "<div class=\"content\">\n"
    body_html += content
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    pubs_html  = "<!DOCTYPE html>\n"
    pubs_html += "<html lang=\"en\">\n"
    pubs_html += head_html + "\n\n"
    pubs_html += body_html
    pubs_html += "</html>\n"

    return inspect.cleandoc(add_links(pubs_html, links))


if __name__ == "__main__":
    cleanup()

    # Load json files
    status("Loading json files:")

    meta_json = read_data('data/meta.json', optional=False)
    fail_if_not("name"        in meta_json, "Must include a \"name\" in data/meta.json!")
    fail_if_not("description" in meta_json, "Must include a \"description\" in data/meta.json!")
    fail_if_not("favicon"     in meta_json, "Must include a \"favicon\" in data/meta.json!")


    style_json = read_data('data/style.json', optional=False)
    fail_if_not("font-color"       in style_json, "Must include a \"font-color\" in data/style.json!")
    fail_if_not("background-color" in style_json, "Must include a \"background-color\" in data/style.json!")
    fail_if_not("header-color"     in style_json, "Must include a \"header-color\" in data/style.json!")
    fail_if_not("accent-color"     in style_json, "Must include a \"accent-color\" in data/style.json!")
    fail_if_not("link-hover-color" in style_json, "Must include a \"link-hover-color\" in data/style.json!")
    fail_if_not("divider-color"    in style_json, "Must include a \"divider-color\" in data/style.json!")

    fail_if_not("paper-img"  in style_json, "Must include a \"paper-img\" in data/style.json!")
    fail_if_not("extra-img"  in style_json, "Must include a \"extra-img\" in data/style.json!")
    fail_if_not("slides-img" in style_json, "Must include a \"slides-img\" in data/style.json!")

    fill_if_missing(style_json, "font-color-dark",       style_json["font-color"])
    fill_if_missing(style_json, "background-color-dark", style_json["background-color"])
    fill_if_missing(style_json, "header-color-dark",     style_json["header-color"])
    fill_if_missing(style_json, "accent-color-dark",     style_json["accent-color"])
    fill_if_missing(style_json, "link-hover-color-dark", style_json["link-hover-color"])
    fill_if_missing(style_json, "divider-color-dark",    style_json["divider-color"])
    fill_if_missing(style_json, "paper-img-dark",        style_json["paper-img"])
    fill_if_missing(style_json, "extra-img-dark",        style_json["extra-img"])
    fill_if_missing(style_json, "slides-img-dark",       style_json["slides-img"])


    profile_json = read_data('data/profile.json', optional=False)
    fail_if_not("headshot" in profile_json, "Must include a \"headshot\" field in data/profile.json!")
    fail_if_not("blurb"    in profile_json, "Must include a \"blurb\" field in data/profile.json!")
    fail_if_not("cv"       in profile_json, "Must include a \"cv\" field in data/profile.json!")
    fail_if_not("email"    in profile_json, "Must include a \"email\" field in data/profile.json!")
    fail_if_not("scholar"  in profile_json, "Must include a \"scholar\" field in data/profile.json!")


    # These next four can be empty
    news_json = read_data('data/news.json', optional=True)
    for news in news_json:
        fail_if_not("date" in news, "Must include a \"date\" field for each news in data/news.json!")
        fail_if_not("text" in news, "Must include a \"text\" field for each news in data/news.json!")

    dates = [datetime.strptime(n["date"], '%m/%Y') for n in news_json]
    warn_if_not(dates == sorted(dates, reverse=True), "The dates in data/news.json are not in order.")


    pubs_json = read_data('data/pubs.json', optional=True)
    for pub in pubs_json:
        fail_if_not("title"      in pub, "Must include a \"title\" field for each pub in data/pubs.json!")
        fail_if_not("conference" in pub, "Must include a \"conference\" field for each pub in data/pubs.json!")
        fail_if_not("authors"    in pub, "Must include a \"authors\" field for each pub in data/pubs.json!")

        fill_if_missing(pub, "link")
        fill_if_missing(pub, "extra")
        fill_if_missing(pub, "slides")

        fail_if_not("section"  in pub, "Must include a \"section\" field for each pub in data/pubs.json!")
        fail_if_not("selected" in pub, "Must include a \"selected\" field for each pub in data/pubs.json!")


    students_json = read_data('data/students.json', optional=True)
    for student in students_json:
        fail_if_not("name"    in student, "Must include a \"name\" field for each student in data/students.json!")
        fail_if_not("project" in student, "Must include a \"project\" field for each student in data/students.json!")
        fail_if_not("result"  in student, "Must include a \"result\" field for each student in data/students.json!")


    auto_links_json = read_data('data/auto_links.json', optional=True)


    # Sanity checks
    status("\nPerforming sanity checks:")
    check_cname()

    fill_if_missing(meta_json, "tracker")
    check_tracker()


    # Load templates
    status("\nLoading template files:")
    main_css    = read_template(f'{TEMPLATES}/main.css',    optional=False)
    head_html   = read_template(f'{TEMPLATES}/head.html',   optional=False)
    footer_html = read_template(f'{TEMPLATES}/footer.html', optional=False)

    footer_html = "\n" + footer_html if not is_federicos() else """\n<footer>\n<p>Feel free to <a href="https://github.com/FedericoAureliano/FedericoAureliano.github.io">use this website template</a>.</p>\n</footer>\n"""


    # Create HTML and CSS
    head_html   = replace_placeholders(head_html, meta_json)
    footer_html = replace_placeholders(footer_html, meta_json)
    main_css    = replace_placeholders(main_css, style_json)
    index_page  = build_index(profile_json, news_json, pubs_json, students_json, auto_links_json)
    news_page   = build_news_page(news_json, auto_links_json)
    pubs_page   = build_pubs_page(pubs_json, auto_links_json)

    # Write to files
    status("\nWriting website:")
    write_file(f'{TARGET}/index.html', index_page)
    write_file(f'{TARGET}/news.html',  news_page)
    write_file(f'{TARGET}/pubs.html',  pubs_page)
    write_file(f'{TARGET}/main.css',   main_css)


    # Got to here means everything went well
    msg = f"Open {TARGET}/index.html in your browser to see your website!"
    success(msg)
    exit(0)