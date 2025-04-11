from flask import Blueprint, render_template

main_controller = Blueprint('main', __name__)

@main_controller.route("/")
def index():
    title = "Newton Cuff"
    titleHeader = "Welcome"
    titleSubHeader = "Here you will find a collection of my thoughts, passions, delusions and interest!"
    return render_template("home.html", title=title, titleHeader =titleHeader, titleSubHeader=titleSubHeader)
