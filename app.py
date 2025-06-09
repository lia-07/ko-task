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

    def __tick(self):
        self.__add_timestamp()
        self.__ticked = True

    def __untick(self):
        self.__remove_timestamp()
        self.__ticked = False

    def __add_timestamp(self):
        now = datetime.now().strftime('%H:%M')
        self.__content += f" <small>{now}</small>"

    def __remove_timestamp(self):
        self.__content = self.__content[:-21]

    # setter for ticked attribute
    def toggle(self):
        if self.__ticked:
            self.__untick()
        else:
            self.__tick()

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
            err = "Couldn't find today's daily note, and a default one wasn't specified."
            print(f"Error: {err}")
            return render_template("Error.html", status=500, error="Internal Server Error", error_body=err), 500

        shutil.copyfile(f"{daily_notes}/Default.md", f"{daily_notes}/{today}.md")

    with open(f"{daily_notes}/{today}.md") as note:
        items = ''
        for i,line in enumerate(note):
            # CHECK IF FILE IS EMPTY
            if line.startswith("- ["):
                # line is a list item
                item = ListItem(line)
                items += item.to_html(i, today)
            elif line.startswith("***") or line.startswith("---"):
                # line is a divider
                items += "<tr><td><hr></td><td</td><tr>\n"
    return render_template("KoboTask.html", today=today, items=items)

@app.route('/tick/<today>/<i>/<t>', methods=['POST'])
def TickItem(today, i, t):
    with open(f"{daily_notes}/{today}.md") as note:
        items = note.readlines()

    if int(i) < 0 or int(i) > (len(items)-1):
        return "<h1>Error: List item number is out of bounds.</h1>"

    item = ListItem(items[int(i)])

    if (t == "untick" and item.is_ticked()) or (t == "tick" and not item.is_ticked()):
        item.toggle()

    items[int(i)] = item.to_md()

    with open(f"{daily_notes}/{today}.md", 'w', encoding='utf-8') as note:
        note.writelines(items)

    return redirect("/#")
