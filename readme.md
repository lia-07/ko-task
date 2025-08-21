# Ko-Task

A simple to-do list web application I made for use on my Ko- Clara eReader, with an extremely lightweight client designed for and tested on the very limited built-in Ko- browser. Designed to integrate with my daily notes in [Obsidian](https://obsidian.md) by using Markdown files in a specified directory as a database (you don't need to use Obsidian for this to work).

<img src="https://github.com/user-attachments/assets/aaf12fa3-529c-4c28-9a51-5ddf3a61bd82" alt="Ko-Task in action." height="320px" width="240">

# Setup

Make sure you have [Python3](https://www.python.org/downloads/) and [Flask](https://flask.palletsprojects.com/en/stable/) installed.

Specify the path of your Daily Notes directory with the environment variable `DAILY_NOTES_DIR`. On my macOS machine I inserted the following line in my `~/.zshrc` file so it's always loaded: `export DAILY_NOTES_DIR="$obsidian_vault/Daily"` (with `$obsidian_vault` already being defined as the path to my Obsidian vault). Note that you may need to apply these changes by sourcing your shell's configuration file (i.e. by running `source ~/.zshrc` or something equivalent).

Create a `Default.md` file inside your daily notes directory containing whichever items you want the application to load if a to-do list for the current date doesn't exist. Make sure to use Markdown checkboxes (i.e. "- [ ] Content") for each item, and that the names of your daily notes are in the "YYYY-MM-DD" format (followed by `.md`, of course).

Then simply run `flask run --port [port of your choosing] --host=0.0.0.0`. The application should now be accessible to all devices on the same network.

I keep my macOS laptop "awake" while plugged in so it can still serve the application using the `caffeinate` command-line utility.

# Warning

This application uses absolutely no authentication whatsoever, meaning anyone on the same network that you serve it on can tick your list items on and off. **In its current form (which I have no intention of drastically changing) this application should _never_ be exposed to the wider internet.**
