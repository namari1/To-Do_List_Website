from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField, DateField

api_key = "1409ab55b133eccc735f7d9816619015"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///lists.db"

db = SQLAlchemy(app)

# CONFIGURE TABLES
app.app_context().push()


# Define a custom 'min' filter
@app.template_filter('min')
def filter_min(value, arg):
    return min(value, arg)


class Lists(db.Model):
    __tablename__ = "Lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    tasks = relationship("Tasks", back_populates="list")


class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.String(250))
    label = db.Column(db.String(250))

    list_id = db.Column(db.Integer, db.ForeignKey("Lists.id"), nullable=False)
    list = relationship("Lists", back_populates="tasks")


class AddList(FlaskForm):
    name = StringField(label="List Name")
    add_list = SubmitField(label="Add List")


class AddTask(FlaskForm):
    name = StringField(label="Task")
    due_date = DateField(label="Due Date")
    # consider making label multiple select field
    label = StringField(label="Label")
    add_task = SubmitField(label="Add Task")


class EditListForm(FlaskForm):
    new_name = StringField(label="New List Name")
    edit_list = SubmitField(label="Edit List")


class EditTaskForm(FlaskForm):
    new_name = StringField(label="New Task Name")
    new_due_date = DateField(label="Due Date")
    new_label = StringField(label="Label")
    edit_task = SubmitField(label="Edit Task")


# all_tasks = Tasks.query.all()
# for task in all_tasks:
#     db.session.delete(task)
# all_lists = Lists.query.all()
# for list in all_lists:
#     db.session.delete(list)
# completed_tasks = Lists(name="Completed Tasks")
# db.session.add(completed_tasks)
# db.session.commit()

@app.route("/")
def home():
    all_lists = Lists.query.filter(Lists.name != "Completed Tasks").all()
    all_tasks = Tasks.query.all()
    return render_template("home_page.html", lists=all_lists, tasks=all_tasks)


@app.route("/add_list", methods=["GET", "POST"])
def add_list():
    form = AddList()
    if form.validate_on_submit():
        list_name = form.name.data
        new_list = Lists(
            name=list_name
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_list.html", form=form)


@app.route('/edit_list', methods=["GET", "POST"])
def edit_list():
    form = EditListForm()
    list_id = request.args.get("id")
    list_selected = Lists.query.get(list_id)
    if form.validate_on_submit():
        list_selected.name = form.new_name.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit_list.html", form=form, list=list_selected)


@app.route("/delete_list")
def delete_list():
    list_id = request.args.get("id")
    list_to_delete = Lists.query.get(list_id)
    list_tasks = Tasks.query.filter_by(list_id=list_id).all()
    for task in list_tasks:
        db.session.delete(task)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add_task/<int:list_id>", methods=["GET", "POST"])
def add_task(list_id):
    form = AddTask()
    list_to_add_task = Lists.query.get(list_id)
    if form.validate_on_submit():
        task_name = form.name.data
        due_date = form.due_date.data
        due_date = due_date.strftime("%m/%d/%Y")
        label = form.label.data
        new_task = Tasks(
            name=task_name,
            due_date=due_date,
            label=label,
            list=list_to_add_task
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_task.html", form=form)


@app.route('/edit_task', methods=["GET", "POST"])
def edit_task():
    form = EditTaskForm()
    task_id = request.args.get("id")
    task_selected = Tasks.query.get(task_id)
    if form.validate_on_submit():
        task_selected.name = form.new_name.data
        due_date = form.new_due_date.data
        due_date = due_date.strftime("%m/%d/%Y")
        task_selected.due_date = due_date
        task_selected.label = form.new_label.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit_task.html", form=form, task=task_selected)


@app.route("/delete_task")
def delete_task():
    task_id = request.args.get("id")
    task_to_delete = Tasks.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/complete_task")
def complete_task():
    completed_tasks_list = Lists.query.filter_by(name="Completed Tasks").all()
    if completed_tasks_list:
        task_id = request.args.get("id")
        task_to_complete = Tasks.query.get(task_id)
        task_to_complete.list_id = completed_tasks_list[0].id
        db.session.commit()
    return redirect(url_for('home'))


@app.route("/completed_tasks")
def show_completed_tasks():
    completed_tasks_list = Lists.query.filter_by(name="Completed Tasks").all()
    completed_tasks = completed_tasks_list[0].tasks
    return render_template("completed_tasks.html", tasks=completed_tasks)


if __name__ == '__main__':
    app.run(debug=True)
