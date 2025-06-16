from flask import Flask, redirect, render_template
from datetime import date, datetime
import os
import shutil

app = Flask(__name__)

daily_notes = os.getenv('DAILY_NOTES_DIR')

class ListItem:
    def __init__(self, md_item):
        self.__content = md_item[6:].rstrip()
        self.__ticked = True if md_item[3] == "x" else False

    def __add_timestamp(self):
        now = datetime.now().strftime('%H:%M')
        self.__content += f" <small>{now}</small>"

    def __remove_timestamp(self):
        self.__content = self.__content.split("<")[0].rstrip()

    def tick(self, timestamp):
        if timestamp and not (len(self.__content) > 20 and self.__content[-20] == "<" and self.__content[-1] == ">"):
            self.__add_timestamp()
        self.__ticked = True

    def untick(self):
        if len(self.__content) > 20 and self.__content[-20] == "<" and self.__content[-1] == ">":
            self.__remove_timestamp()

        self.__ticked = False

    # getter for ticked attribute
    def is_ticked(self):
        return self.__ticked

    # getter for content attribute
    def get_content(self):
        return self.__content

    def to_md(self):
        return f"- [{'x' if self.__ticked else ' '}] {self.__content}\n"

    def to_html(self, i, today):
        return render_template("ListItem.html", ticked=self.__ticked, text=self.__content, i=i, today=today)

@app.route('/')
def TaskList():
    today = date.today().strftime('%Y-%m-%d')

    # create a new daily note for today based on the default one if none exists
    if os.path.isfile(f"{daily_notes}/{today}.md") == False:
        # inform the user if today's daily note doesn't exist and no default one was specified
        if os.path.isfile(f"{daily_notes}/Default.md") == False:
            return http_exception("500 Internal Server Error: Couldn't find today's daily note, and a default one wasn't specified. Make sure you have specified your daily notes directory as an environment variable, and created 'Default.md' within it.")

        shutil.copyfile(f"{daily_notes}/Default.md", f"{daily_notes}/{today}.md")

    with open(f"{daily_notes}/{today}.md") as note:
        items = ''
        for i,line in enumerate(note):
            # CHECK IF FILE IS EMPTY
            if line.startswith("- ["):
                # line is a list item
                item = ListItem(line)

                # ensure unticked items don't have timestamps
                if not item.is_ticked():
                    item.untick()

                items += item.to_html(i, today)
            elif line.startswith("***") or line.startswith("---"):
                # line is a divider
                items += "<tr><td><hr></td><td</td><tr>\n"
        if items == '':
            items += "<tr><td></td><td><i>No todo items for today.</i></td><tr>\n"
    return render_template("KoboTask.html", today=today, items=items)

@app.route('/tick/<today>/<i>/<t>', methods=['POST'])
def TickItem(today, i, t):
    with open(f"{daily_notes}/{today}.md") as note:
        items = note.readlines()

    if int(i) < 0 or int(i) > (len(items)-1):
        return http_exception("416 Request Range Not Satisfiable: No item exists at the specified index (out of bounds).")

    item = ListItem(items[int(i)])

    match t:
        case "untick":
            item.untick()
        case "tick" if not item.is_ticked():
            item.tick(True)
        # if an item is already ticked, don't add a timestamp
        case "tick" if item.is_ticked():
            item.tick(False)

    items[int(i)] = item.to_md()

    with open(f"{daily_notes}/{today}.md", 'w', encoding='utf-8') as note:
        note.writelines(items)

    return redirect("/#")


@app.errorhandler(Exception)
def http_exception(e):
    e = str(e)
    status = int(e[0:3])
    error = e.split(":")[0][4:]
    message = e.split(":")[1][1:]
    print(f"Error: {message}")

    return render_template('Error.html', status=status, error=f"Error {status}: {error}", error_body=message), status
