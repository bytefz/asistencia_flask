import datetime
import pandas as pd

from app import app
from app import db
from flask import flash
from flask import Markup
from flask import url_for
from flask import request
from flask import redirect
from flask import render_template
from constants import FILES_DIR
from constants import DICC_MONTHS
from constants import LOCATIONS
from psycopg2 import DatabaseError
from utilities import DataConverter
from utilities import DataManagment
from flask_login import login_user
from flask_login import current_user
from flask_login import logout_user
from flask_login import login_required
from models.models import FileLoader
from models.models import Assistance
from models.models import FilterForm
from models.models import RegisterForms
from models.models import LoginForm, PageRegisterForm


# Base URL redirect to login 
@app.route('/')
def index():
    return redirect("login"), 302

@app.route('/register', methods=["GET", "POST"])
def registro():

    form = PageRegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():

            register_user = {
                "email": form.email.data,
                "email_confirmed_at": datetime.datetime.now(),
                "password": form.password.data,
                "is_active": True,
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "work_id": form.work_id.data,
                "role_id": 2
            }
            
            # Verificando si el usuario ya ha sido creado
            user = RegisterForms.get_by_email(register_user["email"])
            if user is not None:
                error = Markup(f"El email \"<strong>{register_user['email']}</strong>\" ya está siendo usado por otro usuario")
                flash(error)
            else:
                user = RegisterForms(email=register_user["email"], 
                                    email_confirmed_at=register_user["email_confirmed_at"],
                                    password=register_user["password"],
                                    active=register_user["is_active"],
                                    first_name=register_user["first_name"],
                                    last_name=register_user["last_name"],
                                    work_id=register_user["work_id"],
                                    role_id=register_user["role_id"])
                user.set_password(register_user["password"])
                user.save()
                
                registration_success = "Registro Exitoso"
                flash(registration_success)
                return redirect(url_for("login")), 302
    return render_template('registro/registro.html', form=form), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('main')), 302
    
    form = LoginForm()    

    if request.method == "POST":
        if form.validate_on_submit():
            
            login_user_dict = {
                "email"   : form.email.data,
                "password": form.password.data,
                "remember": form.remember.data
            }
            user = RegisterForms.get_by_email(login_user_dict["email"])
            # Si el correo no existe
            if user is None:
                error = f"Usuario no encontrado"
                flash(error)
            else:
                # Si la contraseña concuerda con la ingresada
                if user.check_password(login_user_dict["password"]):
                    login_user(user, remember=login_user_dict["remember"])
                    return redirect(url_for("main")), 302
                else: 
                    error = f"La contraseña ingresada es  inválida"
                    flash(error)
    return render_template('login/login.html', form=form, request=request), 200

@app.route('/main', methods=["GET", "POST"])
@login_required
def main():
    form = FileLoader()
    filter_form = FilterForm()
    
    # Query to get all the assistance data
    query = """select e.employee_id, e.first_name, e.last_name, concat(e.first_name, ' ' , e.last_name) full_name,  l.place, a."month",a.arrive_hour, a."date"   from employee e 
                inner join locations l  on l.id=e.location_id 
                inner join assistance a on  a.employee_id = e.employee_id;"""
    
    table_assistance = db.session.execute(query).all()
    table_assistance = pd.DataFrame(table_assistance, columns=["employee_id", "first_name", "last_name", "full_name", "location", "month", "arrive_hour", "date"])
    table_assistance["arrive_time"] = table_assistance["arrive_hour"].apply(lambda x: datetime.datetime.strptime(x, "%X %p"))
    
    table_assistance.to_excel(f"{FILES_DIR}/data.xlsx")
    # Define a default dataframe for not showing all data.
    table_assistance_default = table_assistance.loc[(table_assistance["employee_id"] == int(filter_form.employee_name.default))]
    
    if request.method == "POST":
    # Get any filter table
        # Change default filter to form sent by the user
        filter_form.employee_name.default = filter_form.employee_name.data
        filter_form.location.default = filter_form.location.data
        filter_form.month.default = filter_form.month.data
        print(f"""Valores Filtro:\n Valor 'employee_name':{filter_form.employee_name.data}\n Valor 'location':{filter_form.location.data}\n Valor 'month':{filter_form.month.data}""")

        if filter_form.employee_name.data == "None":
            table_assistance = table_assistance.loc[table_assistance["employee_id"]=="None"]
            return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance), 200
        
        # Filter table by the form sent by the user
            # Convert values sent by user to values soported
        location_sent = [value for name, value in LOCATIONS.items() if int(filter_form.location.data)==name]
        month_sent = [value for name, value in DICC_MONTHS.items() if int(filter_form.month.data)==name]

        if int(filter_form.employee_name.data) == 0 and int(filter_form.location.data) == 0:
            table_assistance = table_assistance.loc[(table_assistance["month"] == month_sent[0])]
            return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance), 200
        
        if int(filter_form.employee_name.data) == 0:
            table_assistance = table_assistance.loc[(table_assistance["location"] == location_sent[0]) & (table_assistance["month"] == month_sent[0])]
            return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance), 200
        
        if int(filter_form.location.data) == 0:
            table_assistance = table_assistance.loc[(table_assistance["employee_id"] == int(filter_form.employee_name.data)) & (table_assistance["month"] == month_sent[0])]
            return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance), 200
        
        table_assistance = table_assistance.loc[(table_assistance["employee_id"] == int(filter_form.employee_name.data)) & (table_assistance["location"] == location_sent[0]) & (table_assistance["month"] == month_sent[0])]
        
        return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance), 200
    
    return render_template('main/main.html', form=form, filter_form=filter_form , table=table_assistance_default), 200

@app.route('/file-added', methods=["POST"])
@login_required
def file_added():
    
    form = FileLoader()
    data_manager = DataManagment()
    
    if form.validate_on_submit():
        
        file_oficina_principal = form.file_oficina_principal.data
        file_nicollini = form.file_nicollini.data
        file_ferretero = form.file_ferretero.data
        
        # Files Dicc
        dicc_files = {
            "oficina_principal": file_oficina_principal,
            "nicollini":file_nicollini,
            "ferretero": file_ferretero
        }
        
        # Conditionals
        files = file_oficina_principal or file_ferretero or file_nicollini
        
        # If it does exist any file
        if files:
            # Delete all files before adding another one
            deleted_files = data_manager._delete_files(FILES_DIR)
            
            # If it cannot delete files
            if deleted_files:
                # Store the file
                for name, file in dicc_files.items():
                    
                    if file:
                        
                        format_file = str(file.filename).split(".")[-1]
                        
                        # If format file is ".dat"
                        if format_file == "dat":
                            # filename = secure_filename(file.filename)
                            filename = f"{name}.dat"
                            file.save(FILES_DIR/filename)
                            
                        else:
                            flash("Must be .dat files")
                            return redirect(url_for("main")), 302
                        
                    else:
                        print(f"{name} es {file}")
                        
                return redirect(url_for("dat_converter")), 302
            
            else:
                flash("""There was an error uploading files. Please try again\n
                        If the error persists, contact support.""")
                return redirect(url_for("main")), 302

        # If it does not exist any file
        if files is None:
            error = "Missing a file to upload"
            flash(error, category="error")
            return redirect(url_for("main")), 302


@app.route("/dat-converter", methods=["GET", "POST"])
@login_required
def dat_converter():
    
    # Get dicc paths
    datfiles_list = list(FILES_DIR.glob("*.dat"))
    datfiles_dicc = {data.name.split(".")[0]:data 
                    for data in datfiles_list}
    
    length_datfiles_list = datfiles_dicc.__len__()
    
    # Dataframes 
    df = None
    df_datfiles_list_newcolumn = []
    
    # Processing Dataframes
        # Tranform each ".dat" file to DataFrame
    for name, file in datfiles_dicc.items():
        
        # Adding new columns: "place"
        match name:
            case "oficina_principal":
                
                df_temporary = DataConverter._reader_dat(file)
                # df.insert(index column, name column, value to add, allow_duplicates=False )
                df_temporary.insert(2, "place", 2 ,allow_duplicates=False) # Es mutable
                df_datfiles_list_newcolumn.append(df_temporary) 
            case "nicollini":
                
                df_temporary = DataConverter._reader_dat(file)
                df_temporary.insert(2, "place", 3 ,allow_duplicates=False)
                df_datfiles_list_newcolumn.append(df_temporary) 
            case "ferretero":
                
                df_temporary = DataConverter._reader_dat(file)
                df_temporary.insert(2, "place", 4 ,allow_duplicates=False)
                df_datfiles_list_newcolumn.append(df_temporary)  

        # Delete useless columns
    index_columns = [[3,4,5,6]]*length_datfiles_list
    df_datfiles_deleted_columns_list = list(map(DataManagment.delete_columns_by_index, df_datfiles_list_newcolumn, index_columns))
    
    # If there's more than one file
    if length_datfiles_list > 1:
        for i in range(length_datfiles_list - 1):
            if df is None:
                df = pd.concat([df_datfiles_deleted_columns_list[i], df_datfiles_deleted_columns_list[i+1]], ignore_index=True)
            else:
                df = pd.concat([df, df_datfiles_deleted_columns_list[i+1]], ignore_index=True)
    else:
        df = df_datfiles_deleted_columns_list[0]
    
    # Sort and creating nedded columns: "month"
    df.columns = ["employee_id", "arrive_time", "location"]
    df["arrive_time"] = pd.to_datetime(df["arrive_time"], format="%Y-%m-%d %H:%M:%S")
        # Create month column: str | format: Str Month
    df["month"] = df["arrive_time"].apply(lambda m: m.strftime("%B"))
        # Create arrive_hour column: str | format = 00:00:00 AM/PM
    df["arrive_hour"] = df["arrive_time"].apply(lambda d: d.time().strftime(format="%X %p"))
        # Create date column: str | format: %Y-%m-%d
    df["date"] = df["arrive_time"].apply(lambda d: d.date().strftime(format="%d-%m-%Y"))
    
    # Split data for change values
    data_to_change = df.loc[df["employee_id"]==13]
    df.drop(df[df["employee_id"]==13].index, inplace=True)
    
    data_to_change["arrive_hour"] = data_to_change["arrive_hour"].apply(DataConverter._change_values)
    
    data_to_change.reset_index(inplace=True)
    df.reset_index(inplace=True)
    
    # Concat Dataframes
    df = pd.concat([df,data_to_change], axis=0)
    df.drop(["index"],axis=1 , inplace=True)
    
    # antes pensaba en que iba a defraudar a mi padre por no seguir su carrera: electrónica*
    # Save all data in the database
    Assistance.save_assistance(df)
    
    return redirect(url_for("main")), 302


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index")), 302

# Error Pages

@app.errorhandler(404)
def page_404(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(DatabaseError)
def page_500(error):
    return render_template("errors/500.html"), 500


# Custom Filters

    # Custom Filter to convert str to datetime format
@app.template_filter('date')
def date_filter(s, format):
    return datetime.datetime.strptime(s, format)

    # Custom Filter to return the month form a datetime object
@app.template_filter('month')
def month_filter(s):
    return datetime.datetime.strftime(s, "%B")

    # Custom filter to strip a str
@app.template_filter("strip")
def str_strip(s:str):
    return s.strip()

    # Custom filter to get the actual time
@app.template_filter("now")
def now_time(s):
    return datetime.datetime.now().strftime("%H_%M_%S__%d_%m_%Y")