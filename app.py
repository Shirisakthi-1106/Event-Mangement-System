from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  
import psycopg2 
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:SYS@localhost:5432/college_event_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(50), nullable=False)
    event_location = db.Column(db.String(100), nullable=False)
    event_description = db.Column(db.String(255))
    

    def __repr__(self):
        return f'<Event {self.event_name}>'

# Budget model
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))

    event = db.relationship('Event', backref='budgets')

    def __repr__(self):
        return f'<Budget for Event ID {self.event_id}>'

# Sponsor model
class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)

    event = db.relationship('Event', backref='sponsors')

    def __repr__(self):
        return f'<Sponsor {self.name}>'

# Resource model
class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)

    event = db.relationship('Event', backref='resources')

    def __repr__(self):
        return f'<Resource {self.resource_name}>'
    



    

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='college_event_management',
            user='postgres',
            password='SYS'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None 



@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        description = request.form['description']
        
       
        try:
            db.session.execute(
                text("SELECT create_event(:event_name, :event_date, :event_location, :event_description)"),
                {
                    'event_name': name,
                    'event_date': date,
                    'event_location': location,
                    'event_description': description
                }
            )
            db.session.commit()
            flash('Event added successfully.')
        except Exception as e:
            db.session.rollback()
            flash('Error adding event: ' + str(e))
        
        return redirect(url_for('events'))
    
    return render_template('add_event.html')



@app.route('/events')
def events():
    all_events = Event.query.all()
    return render_template('events.html', events=all_events)
@app.route('/event/<int:event_id>')
def event_details(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))

    # Retrieve budgets, sponsors, and resources associated with the event
    budgets = Budget.query.filter_by(event_id=event_id).all()
    sponsors = Sponsor.query.filter_by(event_id=event_id).all()
    resources = Resource.query.filter_by(event_id=event_id).all()

    print(resources) 

    # Prepare lists for rendering in the template
    budget_list = [{
        'id': budget.id,
        'amount': budget.amount,
        'description': budget.description
    } for budget in budgets]

    sponsor_list = [{
        'id': sponsor.id,
        'name': sponsor.name,
        'description': sponsor.description
    } for sponsor in sponsors]

    resource_list = [{
        'id': resource.id,
        'name': resource.resource_name,
        'type': resource.resource_type
    } for resource in resources]

    return render_template('event_details.html', event=event, budgets=budget_list, sponsors=sponsor_list, resources=resource_list)


@app.route('/event/<int:event_id>/add_budget', methods=['GET', 'POST'])
def add_budget(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))

    if request.method == 'POST':
        amount = request.form['amount']
        description = request.form['description']

        conn=None
        cursor=None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("CALL add_event_budget(%s, %s, %s)", (event_id, amount, description))
            conn.commit()
            flash('Budget added successfully.')
        except Exception as e:
            flash(f'Error adding budget: {e}')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('event_details', event_id=event_id))

    return render_template('add_budget.html', event=event)


@app.route('/event/<int:event_id>/add_sponsor', methods=['GET', 'POST'])


@app.route('/event/<int:event_id>/add_sponsor', methods=['GET', 'POST'])
def add_sponsor(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))  # Adjust this to your event listing route

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not description:
            flash('Name and description are required fields.')
            return redirect(url_for('add_sponsor', event_id=event_id))  # Redirect back to the form

        # Call the stored procedure 'add_event_sponsor'
        try:
            # Using the db connection to call the procedure with text()
            db.session.execute(
                text("CALL add_event_sponsor(:event_id, :name, :description)"),
                {"event_id": event_id, "name": name, "description": description}
            )
            db.session.commit()

            flash('Sponsor added successfully.')
            return redirect(url_for('event_details', event_id=event_id))  # Redirect to the event details page
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('add_sponsor', event_id=event_id))

    return render_template('add_sponsor.html', event=event)

@app.route('/event/<int:event_id>/add_resource', methods=['GET', 'POST'])
def add_resource(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))

    if request.method == 'POST':
        name = request.form['name']
        resource_type = request.form['resource_type']

        try:
            # Call the stored procedure 'add_event_resource'
            db.session.execute(
                text("CALL add_event_resource(:event_id, :name, :resource_type)"),
                {"event_id": event_id, "name": name, "resource_type": resource_type}
            )
            db.session.commit()
            flash('Resource added successfully.')
            return redirect(url_for('resources', event_id=event_id))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}")
            return redirect(url_for('add_resource', event_id=event_id))

    return render_template('add_resource.html', event=event)

@app.route('/event/<int:event_id>/resources')
def resources(event_id):
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))

    resources = Resource.query.filter_by(event_id=event_id).all()
    return render_template('resources.html', event=event, resources=resources)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    try:
        # Call the stored procedure to delete the event
        db.session.execute(text("CALL delete_event(:event_id)"), {'event_id': event_id})
        db.session.commit()  # Commit the transaction after the stored procedure is executed
        flash('Event and its associated data deleted successfully.')
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        flash(f'Error deleting event: {str(e)}')

    return redirect(url_for('events'))  # Redirect to the events page after deletion


@app.route('/delete_sponsor/<int:sponsor_id>', methods=['POST'])
def delete_sponsor(sponsor_id):
    try:
        # Call the stored procedure to delete the sponsor
        db.session.execute(text("CALL delete_sponsor(:sponsor_id)"), {'sponsor_id': sponsor_id})
        db.session.commit()  # Commit the transaction after the stored procedure is executed
        flash('Sponsor deleted successfully.')
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        flash(f'Error deleting sponsor: {str(e)}')

    # Redirect to the event details page or the events page
    sponsor = Sponsor.query.get(sponsor_id)  # Check if sponsor still exists
    if sponsor:
        event_id = sponsor.event_id  # Store event_id for redirection
        return redirect(url_for('event_details', event_id=event_id))
    else:
        return redirect(url_for('events'))


@app.route('/delete_resource/<int:resource_id>', methods=['POST'])
def delete_resource(resource_id):
    try:
        # Retrieve the resource and the associated event_id before deletion
        resource = Resource.query.get(resource_id)
        if resource:
            event_id = resource.event_id  # Store event_id for redirection

            # Call the stored procedure 'delete_resource' using SQLAlchemy's execute method
            db.session.execute(
                text("CALL delete_resource(:resource_id)"),
                {"resource_id": resource_id}
            )
            # Commit the transaction
            db.session.commit()
            flash('Resource deleted successfully.')
        else:
            flash('Resource not found.')
            event_id = None  # Set event_id to None if resource not found
        
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")
        event_id = None  # Set event_id to None in case of error
    
    # Redirect to the resources page or events page based on event_id
    return redirect(url_for('resources', event_id=event_id) if event_id else url_for('events'))

@app.route('/event/<int:event_id>/delete_budget/<int:budget_id>', methods=['POST'])
def delete_budget(event_id, budget_id):
    try:
        # Retrieve the budget before deletion
        budget = Budget.query.get(budget_id)
        if budget:
            # Call the stored procedure 'delete_budget' using SQLAlchemy's execute method
            db.session.execute(
                text("CALL delete_budget(:budget_id)"),
                {"budget_id": budget_id}
            )
            # Commit the transaction
            db.session.commit()
            flash('Budget deleted successfully.')
        else:
            flash('Budget not found.')
        
    except Exception as e:
        # Rollback the transaction in case of error
        db.session.rollback()
        flash(f"An error occurred: {str(e)}")
    
    # Redirect to the event details page after deletion
    return redirect(url_for('event_details', event_id=event_id))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if request.method == 'POST':
        event_name = request.form['name']
        event_date = request.form['date']
        event_location = request.form['location']
        event_description = request.form['description']
        
        try:
            # Call the stored procedure to update the event
            db.session.execute(text("""
                CALL update_event(:event_id, :event\_name, :event_date, :event_location, :event_description)
            """), {
                'event_id': event_id,
                'event_name': event_name,
                'event_date': event_date,
                'event_location': event_location,
                'event_description': event_description
            })
            db.session.commit()
            flash('Event updated successfully.')
            return redirect(url_for('event_details', event_id=event_id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}')
            return redirect(url_for('events'))
    
    # For GET request, fetch event details to display in the form
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.')
        return redirect(url_for('events'))

    return render_template('edit_event.html', event=event)

@app.route('/events_cursor')
def events_cursor():
   
    cursor = db.session.execute(text("SELECT event_name FROM event"))
    events = cursor.fetchall()

   
    for event in events:
        print(f"Event: {event[0]}")

    return "Check terminal for list of event names"



if __name__ == '__main__':
    app.run(debug=True)
