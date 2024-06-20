from flask import Blueprint, render_template

# Create a Blueprint object for the notes section
notes_bp = Blueprint('notes', __name__)

# Define the route for the /notes endpoint
@notes_bp.route('/notes')
def notes():
    return render_template('n.html')

