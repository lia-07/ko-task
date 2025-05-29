from flask import Flask, redirect, render_template
from datetime import date, datetime
import os
import shutil

app = Flask(__name__)

daily_notes = "/Users/lia/Documents/Obsidian/lias-vault/Daily"

class ListItem:
    def __init__(self, md_item):
        self.text = md_item[6:].rstrip()
        self.ticked = True if md_item[3] == "x" else False

    def tick(self):
        self.add_timestamp()
        self.ticked = True

    def untick(self):
        self.remove_timestamp()
        self.ticked = False

    def add_timestamp(self):
        now = datetime.now().strftime('%H:%M')
        self.text += f" <small>{now}</small>"

    def remove_timestamp(self):
        self.text = self.text[:-21]

    def to_md(self):
        return f"- [{'x' if self.ticked else ' '}] {self.text}\n"

    def to_html(self, i, today):
        str = f"<li><form method='POST' name='{i}' action='/tick/{today}/{i}' onChange='submit();'><input type='checkbox' {'checked' if self.ticked else ''} name='checkbox' ><span>{self.text}</span></form></li>"
        return str

@app.route('/')
def TaskList():
    today = date.today().strftime('%Y-%m-%d')
    if os.path.isfile(f"{daily_notes}/{today}.md") == False:
        shutil.copyfile(f"{daily_notes}/Default.md", f"{daily_notes}/{today}.md")

    with open(f"{daily_notes}/{today}.md") as note:
        items = ''
        for i,line in enumerate(note):
            if line.startswith("- ["):
                item = ListItem(line)
                items += item.to_html(i, today)
            elif line.startswith("***") or line.startswith("---"):
                items += "<hr>\n"
    return render_template("KoboTask.html", today=today, items=items)

@app.route('/tick/<today>/<i>', methods=['POST'])
def TickItem(today, i):
    with open(f"{daily_notes}/{today}.md") as note:
        items = note.readlines()

    item = ListItem(items[int(i)])

    if item.ticked:
        item.untick()
    else:
        item.tick()

    items[int(i)] = item.to_md()

    with open(f"{daily_notes}/{today}.md", 'w', encoding='utf-8') as note:
        note.writelines(items)

    return redirect("/#")
