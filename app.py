from flask import Flask, redirect, render_template
from datetime import date, datetime
import os
import shutil

app = Flask(__name__)

daily_notes = os.getenv('DAILY_NOTES_DIR')

# a class for creating list item objects, which each have a 'content' and 'ticked' attribute
class ListItem:
    def __init__(self, md_item):
        self.__content = md_item[6:].rstrip()
        self.__ticked = True if md_item[3] == "x" else False

    def __add_timestamp(self):
        now = datetime.now().strftime('%H:%M')
        self.__content += f" <small>{now}</small>"

    def __remove_timestamp(self):
        self.__content = self.__content.split("<")[0].rstrip()

    # setter for ticked attribute
    def tick(self, timestamp):
        if timestamp and not (len(self.__content) > 20 and self.__content[-20] == "<" and self.__content[-1] == ">"):
            self.__add_timestamp()
        self.__ticked = True

    # setter for ticked attribute
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

    # returns the object as a markdown string
    def to_md(self):
        return f"- [{'x' if self.__ticked else ' '}] {self.__content}\n"

    # returns the object as an html string
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
        # loop over each line in the file
        for i,line in enumerate(note):

            # check if line is a markdown checklist item, if so create a list item object from it
            if line.startswith("- ["):
                item = ListItem(line)

                # ensure unticked items don't have timestamps
                if not item.is_ticked():
                    item.untick()

                # append html version of the list item to the "items" string
                items += item.to_html(i, today)

            # otherwise, check if the line is a markdown divider, in which case append an html divider to "items"
            elif line.startswith("***") or line.startswith("---"):
                items += "<tr><td><hr></td><td</td><tr>\n"

        # if there are no items in the file, inform the user instead of showing a blank page
        if items == '':
            items += "<tr><td></td><td><i>No todo items for today.</i></td><tr>\n"

    return render_template("Ko-Task.html", today=today, items=items)

@app.route('/tick/<today>/<i>/<t>', methods=['POST'])
def TickItem(today, i, t):

    with open(f"{daily_notes}/{today}.md") as note:
        items = note.readlines()

    # boundary check to make sure the requested item to mutate exists
    if int(i) < 0 or int(i) > (len(items)-1):
        return http_exception("416 Request Range Not Satisfiable: No item exists at the specified index (out of bounds).")

    # make sure that the requested line is actually a list item
    if not items[int(i)].startswith("- ["):
        return http_exception("406 Not Acceptable: Line at index isn't a checkbox.")

    item = ListItem(items[int(i)])

    match t:
        case "untick":
            item.untick()
        case "tick" if not item.is_ticked():
            item.tick(True)
        # if an item is already ticked, don't add a timestamp
        case "tick" if item.is_ticked():
            item.tick(False)

    # save changes to list item
    items[int(i)] = item.to_md()

    # write changes to the daily note
    with open(f"{daily_notes}/{today}.md", 'w', encoding='utf-8') as note:
        note.writelines(items)

    # redirect back to home page
    return redirect("/#")


@app.errorhandler(Exception)
def http_exception(e):
    e = str(e)
    status = int(e[0:3])
    error = e.split(":")[0][4:]
    message = e.split(":")[1][1:]
    print(f"Error: {message}")

    return render_template('Error.html', status=status, error=f"Error {status}: {error}", error_body=message), status
