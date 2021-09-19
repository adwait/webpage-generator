#!python3

import json
import inspect

# Define functions for pieces
def build_news(news, count, standalone):
    if count > len(news):
        count = len(news)

    if count <= 0:
        return ""
    
    print("\nAdding news:")
    news_list = ""

    for n in news[:count]:
        print(n["date"])
        item =  '<div class="news-item">\n'
        item += '<div class="news-left">' + n["date"] + '</div>\n'
        item += '<div class="news-right">' + n["text"] + '</div>\n'
        item += '</div>\n'
        news_list += item

    news_html =  "<div class=\"section\">\n"

    if (count != len(news)):
        link = "<a href=\"./news.html\">See all news</a>"
        news_html += "<h1>Recent News <small style=\"font-weight: 300; float: right; margin-top: 0.23em\">(%s)</small></h1>\n" %link
    elif standalone:
        link = "<a href=\"./index.html\">%s</a>" % meta_json["name"]
        news_html += "<h1>News <small style=\"font-weight: 300; float: right; margin-top: 0.23em\">%s</small></h1>\n" %link
    else:
        news_html += "<h1>News</h1>\n"
    news_html += "<div class=\"hbar\"></div>\n"
    news_html += "<div id=\"news\">\n"
    news_html += news_list
    news_html += "</div>\n" # close news
    news_html += "</div>\n" # close section
    return news_html

# Helper function to decide what publication sections to include
def get_pub_titles(pubs):
    titles = set()
    for p in pubs:
        titles.add(p["section"])
    return sorted(list(titles))

def some_not_selected(pubs):
    for p in pubs:
        if not p["selected"]:
            return True
    return False

def build_pubs_inner(pubs, title, full):
    if title == "":
        return ""

    pubs_list = ""

    for p in pubs:
        if title == p["section"] and (p["selected"] or full):
            print(p["title"])
            item =  '<div class="paper">\n'
            item += '<div class="paper-left">\n'
            item += '<div class="paper-conference">' + p["conference"] + '</div>\n'
            item += '<a href="' + p["link"] + '" alt="[PDF]"><img class="icon" src="%s"/><img class="icon-dark" src="%s"/></a>\n' % (style_json["paper-img"], style_json["paper-img-dark"]) if p["link"] else ""
            item += '<a href="' + p["extra"] + '" alt="[Extra]"><img class="icon" src="%s"/><img class="icon-dark" src="%s"/></a>\n' % (style_json["extra-img"], style_json["extra-img-dark"]) if p["extra"] else ""
            item += '<a href="' + p["slides"] + '" alt="[Slides]"><img class="icon" src="%s"/><img class="icon-dark" src="%s"/></a>\n' % (style_json["slides-img"], style_json["slides-img-dark"]) if p["slides"] else ""
            item += '</div>\n' # close paper-left
            item += '<div class="paper-right">\n'
            item += '<div class="paper-title">' + p["title"] + '</div>\n'
            item += '<div class="paper-authors">' + ",\n".join(p["authors"].split(", ")) + '</div>\n'
            item += '</div>\n' # close paper-right
            item += '</div>\n' # close paper
            pubs_list += item

    pubs_html =  "<h3 id=\"%spublications\">%s</h3>" % (title, title)
    pubs_html += pubs_list
    return pubs_html

def build_pubs(pubs, full):
    if len(pubs) == 0:
        return ""

    print("\nAdding publications:")

    pubs_html =  "<div class=\"section\">\n"
    if some_not_selected(pubs) and not full: 
        pubs_html += "<h1>Selected Publications <small style=\"font-weight: 300; float: right; margin-top: 0.23em\">(<a href=\"./pubs.html\">See all publications</a>)</small></h1>" 
    elif full: 
        link = "<a href=\"./index.html\">%s</a>" % meta_json["name"]
        pubs_html += "<h1>Publications <small style=\"font-weight: 300; float: right; margin-top: 0.23em\">%s</small></h1>\n" %link
    else: 
        pubs_html += "<h1>Publications</h1>"

    pubs_html += "<div class=\"hbar\"></div>\n"
    pubs_html += "<div id=\"publications\">\n"
    titles = get_pub_titles(pubs)
    for i in range(len(titles)):
        title = titles[i]
        pubs_html += build_pubs_inner(pubs, title, full)
        if i != len(titles) - 1:
            pubs_html += "<p style=\"font-size: 0.7em\">&nbsp</p>\n"

    pubs_html += "</div>\n" # close pubs
    pubs_html += "</div>\n" # close section
    return pubs_html

def build_students(students):
    if len(students) == 0:
        return ""

    print("\nAdding students:")
    students_list = ""

    for p in students:
        print(p["name"])
        item =  '<div class="student">\n' + p["name"] + "\n"
        item += '<div class="student-project">' + p["project"] + '</div>\n'
        item += '<div class="student-result">' + p["result"] + '</div>\n'
        item += '</div>\n'
        students_list += item

    students_html =  "<div class=\"section\">\n"
    students_html += "<h1>Mentoring</h1>\n"
    students_html += "<div class=\"hbar\"></div>\n"
    students_html += "<div id=\"students\">\n"
    students_html += students_list
    students_html += "</div>\n" # close students
    students_html += "</div>\n" # close section
    return students_html

def build_profile(profile):
    profile_html =  "<div class=\"profile\">\n"
    profile_html += "<div class=\"profile-left\">\n"
    profile_html += "<img class=\"headshot\" src=\"%s\" alt=\"Headshot\"/>\n" % profile["headshot"]
    profile_html += profile["blurb"]
    profile_html += "\n<p>Here is my "
    profile_html += "<a href=\"%s\">CV</a> and " % profile["cv"]
    profile_html += "<a href=\"%s\">Google Scholar</a>. " % profile["scholar"]
    profile_html += "You can reach me at %s." % profile["email"]
    profile_html += "</p>\n" # close description paragraph
    profile_html += "</div>\n" # close profile-left
    profile_html += "</div>\n" # close profile
    return profile_html

def add_links(html, links):
    print("\nAdding links:")

    toreplace = sorted(links.keys(), key=len, reverse=True)

    for name in toreplace:
        pos = html.find(name)
        while pos != -1:
            prefix = html[:pos]
            suffix = html[pos:]

            open = html[:pos].count("<a href=")
            close = html[:pos].count("</a>")

            print(name, pos, open, close)
            if pos >= 0 and open == close:
                toreplace = "<a href=\"%s\">%s</a>" % (links[name], name)
                suffix = suffix.replace(name, toreplace, 1)
                html = prefix+suffix

            start = len(prefix) + len(toreplace) - len(name)
            tmp = html[start:].find(name)
            pos = tmp + start if tmp >= 0 else tmp
    
    return html

def build_index(profile_json, news_json, pubs_json, students_json, links):
    body_html =  "<body>\n"
    body_html += build_profile(profile_json)
    body_html += build_news(news_json, 5, False)
    body_html += build_pubs(pubs_json, False)
    body_html += build_students(students_json)
    body_html += footer_html
    body_html += "</body>\n"

    index_html =  "<!DOCTYPE html>\n"
    index_html += "<html lang=\"en\">\n"
    index_html += header_html + "\n\n"
    index_html += body_html
    index_html += "</html>\n"

    return inspect.cleandoc(add_links(index_html, links))

def build_news_site(news_json, links):
    body_html =  "<body>\n"
    body_html += build_news(news_json, len(news_json), True)
    body_html += footer_html
    body_html += "</body>\n"

    news_html =  "<!DOCTYPE html>\n"
    news_html += "<html lang=\"en\">\n"
    news_html += header_html + "\n\n"
    news_html += body_html
    news_html += "</html>\n"

    return inspect.cleandoc(add_links(news_html, links))

def build_pubs_site(pubs_json, links):
    body_html =  "<body>\n"
    body_html += build_pubs(pubs_json, True)
    body_html += footer_html
    body_html += "</body>\n"

    pubs_html =  "<!DOCTYPE html>\n"
    pubs_html += "<html lang=\"en\">\n"
    pubs_html += header_html + "\n\n"
    pubs_html += body_html
    pubs_html += "</html>\n"

    return inspect.cleandoc(add_links(pubs_html, links))

def replace_placeholders(text, map):
    newtext = text
    for k in map:
        newtext = newtext.replace(k+"-placeholder", map[k])
    return newtext

# Helper functions for sanity checks
def require(cond, msg):
    if not cond:
        msg = f"ERROR: {msg}"
        divider = "*"*len(msg)
        print(f"\n{divider}\n{msg}\n{divider}\n")
        exit(0)

def optional(json, field, default = ""):
    if not field in json:
        json[field] = default
    return json

# Load json files
with open('data/profile.json') as f:
    try:
        profile_json = json.load(f)
    except Exception as e:
        require(False, "Failed to parse data/profile.json. Maybe check your commas and braces?")

    require("headshot" in profile_json, "Must include a \"headshot\" field in data/profile.json!")
    require("blurb" in profile_json, "Must include a \"blurb\" field in data/profile.json!")
    require("cv" in profile_json, "Must include a \"cv\" field in data/profile.json!")
    require("email" in profile_json, "Must include a \"email\" field in data/profile.json!")
    require("scholar" in profile_json, "Must include a \"scholar\" field in data/profile.json!")

with open('data/meta.json') as f:
    try:
        meta_json = json.load(f)
    except Exception as e:
        require(False, "Failed to parse data/meta.json. Maybe check your commas and braces?")

    require("name" in meta_json, "Must include a \"name\" in data/meta.json!")
    require("description" in meta_json, "Must include a \"description\" in data/meta.json!")
    require("favicon" in meta_json, "Must include a \"favicon\" in data/meta.json!")
    optional(meta_json, "tracker")

with open('data/style.json') as f:
    try:
        style_json = json.load(f)
    except Exception as e:
        require(False, "Failed to parse data/style.json. Maybe check your commas and braces?")

    require("font-color" in style_json, "Must include a \"font-color\" in data/style.json!")
    require("background-color" in style_json, "Must include a \"background-color\" in data/style.json!")
    require("header-color" in style_json, "Must include a \"header-color\" in data/style.json!")
    require("accent-color" in style_json, "Must include a \"accent-color\" in data/style.json!")
    require("link-hover-color" in style_json, "Must include a \"link-hover-color\" in data/style.json!")
    require("divider-color" in style_json, "Must include a \"divider-color\" in data/style.json!")

    require("paper-img" in style_json, "Must include a \"paper-img\" in data/style.json!")
    require("extra-img" in style_json, "Must include a \"extra-img\" in data/style.json!")
    require("slides-img" in style_json, "Must include a \"slides-img\" in data/style.json!")

    optional(style_json, "font-color-dark", style_json["font-color"])
    optional(style_json, "background-color-dark", style_json["background-color"])
    optional(style_json, "header-color-dark", style_json["header-color"])
    optional(style_json, "accent-color-dark", style_json["accent-color"])
    optional(style_json, "link-hover-color-dark", style_json["link-hover-color"])
    optional(style_json, "divider-color-dark", style_json["divider-color"])
    optional(style_json, "paper-img-dark", style_json["paper-img"])
    optional(style_json, "extra-img-dark", style_json["extra-img"])
    optional(style_json, "slides-img-dark", style_json["slides-img"])

# These next four can be empty
try:
    with open('data/news.json') as f:
        news_json = json.load(f)
        for news in news_json:
            require("date" in news, "Must include a \"date\" field for each news in data/news.json!")
            require("text" in news, "Must include a \"text\" field for each news in data/news.json!")
except Exception as e:
    print(e)
    news_json = {}

try:
    with open('data/pubs.json') as f:
        pubs_json = json.load(f)
        for pub in pubs_json:
            require("title" in pub, "Must include a \"title\" field for each pub in data/pubs.json!")
            require("conference" in pub, "Must include a \"conference\" field for each pub in data/pubs.json!")
            require("authors" in pub, "Must include a \"authors\" field for each pub in data/pubs.json!")
            optional(pub, "link")
            optional(pub, "extra")
            optional(pub, "slides")
            require("section" in pub, "Must include a \"section\" field for each pub in data/pubs.json!")
            require("selected" in pub, "Must include a \"selected\" field for each pub in data/pubs.json!")
except Exception as e:
    print(e)
    pubs_json = {}

try:
    with open('data/students.json') as f:
        students_json = json.load(f)
        for student in students_json:
            require("name" in student, "Must include a \"name\" field for each student in data/students.json!")
            require("project" in student, "Must include a \"project\" field for each student in data/students.json!")
            require("result" in student, "Must include a \"result\" field for each student in data/students.json!")

except Exception as e:
    print(e)
    students_json = {}

try:
    with open('data/auto_links.json') as f:
        auto_links_json = json.load(f)
except Exception as e:
    print(e)
    auto_links_json = {}


# Load templates
with open('templates/main.css') as f:
    main_css = f.read()

with open('templates/header.html') as f:
    header_html = f.read()

with open('templates/footer.html') as f:
    footer_html = "\n\n" + f.read() if meta_json["name"] != "Federico Mora Rocha" else ""

# Create HTML and CSS
header_html = replace_placeholders(header_html, meta_json)
footer_html = replace_placeholders(footer_html, meta_json)
main_css    = replace_placeholders(main_css, style_json)
index_html  = build_index(profile_json, news_json, pubs_json, students_json, auto_links_json)
news_site   = build_news_site(news_json, auto_links_json)
pubs_site   = build_pubs_site(pubs_json, auto_links_json)

# Write to files
with open('docs/index.html', 'w') as index:
    index.write(index_html)

with open('docs/news.html', 'w') as index:
    index.write(news_site)

with open('docs/pubs.html', 'w') as index:
    index.write(pubs_site)

with open('docs/main.css', 'w') as main:
    main.write(main_css)

# Got to here means everything went well
msg = "Success! Open docs/index.html in your browser to see your website!"
divider = "*"*len(msg)
print(f"\n{divider}\n{msg}\n{divider}\n")
exit(0)