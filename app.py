
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from sqlalchemy import create_engine, or_, cast, String
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

import os

from models import Base, User, Patient, Suivi, Validation

load_dotenv()

# ============
# Config Flask
# ============
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Config SQLAlchemy

db = os.environ.get('DB')

engine = create_engine(db)

try:

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    print("DB Success!")

except Exception as ex:
    print(ex)

# ==================
# Config Flask-Login
# ==================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

# ====================
# Fonction Flask-Login
# ====================
@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

# ======
# Routes
# ======

# Accueil - Se connecter
@app.route('/', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Vérifier que tous les champs sont remplis
        if not email or not password:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('index'))
        
        # Vérifier si l'utilisateur existe
        user = session.query(User).filter_by(email=email).first()

        if not user:
            flash("Cette adresse mail est inconnue", "error")
            return redirect(url_for('index'))

        # Si l'utilisateur existe et que le mot de passe est juste
        if user and check_password_hash(user.password, password):
            # Connecter l'utilisateur
            login_user(user)
            return redirect('dashboard')
        # Sinon
        else:
            # Mot de passe incorrecte
            flash("Le mot de passe est incorrect.", "error")
            return redirect(url_for('index'))
    
    return render_template('index.html')


# Créer un compte
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        surname = request.form.get('surname').upper()
        first_name = request.form.get('first_name').capitalize()
        enterprise = request.form.get('enterprise')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        # Vérifier que tous les champs sont remplis
        if not surname or not first_name or not enterprise or not email or not password or not confirmation:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('register'))
        
        # Verifier que le password = confirmation
        if password != confirmation:
            flash("Le mot de passe et la confirmation ne correspondent pas.", "error")
            return redirect(url_for('register'))

        #  Verifier que l'email n'existe pas dans la DB
        if session.query(User).filter_by(email=email).first():
            flash("Cette adresse email est déjà enregistrée.", "error")
            return redirect(url_for('register'))
        else:
            # Crypter le password
            hashed_password = generate_password_hash(password)

            # Ajouter l'utilisateur à la DB
            newUser = User(
                surname=surname, 
                first_name=first_name, 
                enterprise=enterprise, 
                email=email, 
                password=hashed_password)
            
            session.add(newUser)
            session.commit()

            flash("Compte créé avec succès ! Connectez-vous pour accéder à votre tableau de bord.", "success")
            return redirect(url_for('index'))
    
    return render_template('register.html')


# Deconnexion
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Tableau de bord
@app.route('/dashboard', methods=["GET"])
@login_required
def dashboard():
    user = session.query(User).filter_by(id=current_user.id).first()

    # Récupérer le terme de recherche
    search = request.args.get("q", "").strip()

    # Si une recherche est faite
    if search:
        patients = session.query(Patient).filter(
        Patient.user_id == current_user.id,
        or_(
            Patient.surname.ilike(f"%{search}%"),
            Patient.first_name.ilike(f"%{search}%"),
            Patient.ipp.ilike(f"%{search}%"),
            Patient.day_of_birthday.ilike(f"%{search}%"),
            Patient.month_of_birthday.ilike(f"%{search}%"),
            Patient.year_of_birthday.ilike(f"%{search}%")
            )
        ).all()
    else:
        # Sinon afficher tous les patients de l’utilisateur
        patients = session.query(Patient).filter_by(user_id=current_user.id).all()

    return render_template("dashboard.html", user=user, patients=patients, search=search)


# Ajouter un patient
@app.route('/add-a-patient', methods=["GET", "POST"])
@login_required
def addAPatient():
    user = session.query(User).filter_by(id=current_user.id).first()

    if request.method == "POST":
        ipp = request.form.get('ipp')
        surname = request.form.get('surname').upper()
        first_name = request.form.get('first_name').capitalize()
        day_of_birthday = request.form.get('day_of_birthday')
        month_of_birthday = request.form.get('month_of_birthday')
        year_of_birthday = request.form.get('year_of_birthday')

        # Vérifier que tous les champs sont remplis
        if not ipp or not surname or not first_name or not day_of_birthday or not month_of_birthday or not year_of_birthday:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('addAPatient', user=user))
        
        # Vérifier que le patient n'existe pas dans la base de données
        if session.query(Patient).filter_by(ipp=ipp, surname=surname, first_name=first_name, day_of_birthday=day_of_birthday, month_of_birthday=month_of_birthday, year_of_birthday=year_of_birthday, user_id=current_user.id).first():
            # Si le patient existe : renvoyer que le patient existe déjà
            flash("Le patient existe déjà", "error")
            return redirect(url_for('addAPatient', user=user))
        else:
            # Si le patient n'existe pas, créer un nouveau patient 
            newPatient = Patient(
                ipp=ipp, 
                surname=surname, 
                first_name=first_name, 
                day_of_birthday=day_of_birthday, 
                month_of_birthday=month_of_birthday, 
                year_of_birthday=year_of_birthday, 
                personnage="Inconnu", 
                end_of_hospitalisation=False, 
                nb_de_jours_de_suivi_post_hospit=0, 
                nb_de_suivi_post_hospit_par_jour=0, 
                user_id=current_user.id)
            
            session.add(newPatient)
            session.commit()

            return redirect(url_for('dashboard', user=user))


    return render_template('add-a-patient.html', user=user)


# Voir la fiche patient
@app.route('/view-patient/<int:patient_id>')
@login_required
def viewPatient(patient_id):
    patient = session.query(Patient).filter_by(id=patient_id).first()

    return render_template('view-patient.html', patient=patient)


# Modifier la fiche patient
@app.route('/edit-patient/<int:patient_id>', methods=["GET", "POST"])
@login_required
def editPatient(patient_id):
    patient = session.query(Patient).filter_by(id=patient_id).first()

    if request.method == "POST":
        ipp = request.form.get('ipp')
        surname = request.form.get('surname').upper()
        first_name = request.form.get('first_name').capitalize()
        day_of_birthday = request.form.get('day_of_birthday')
        month_of_birthday = request.form.get('month_of_birthday')
        year_of_birthday = request.form.get('year_of_birthday')
        end_of_hospitalisation = request.form.get("end_of_hospitalisation")

        # Vérifier que tous les champs sont remplis
        if not ipp or not surname or not first_name or not day_of_birthday or not month_of_birthday or not year_of_birthday or not end_of_hospitalisation:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('editPatient', patient=patient))

        # Modifier les informations dans la base de données
        patient.ipp = ipp
        patient.surname = surname
        patient.first_name = first_name
        patient.day_of_birthday = day_of_birthday
        patient.month_of_birthday = month_of_birthday
        patient.year_of_birthday = year_of_birthday
        patient.end_of_hospitalisation = (end_of_hospitalisation == "1")

        if patient.end_of_hospitalisation:
            # Si c'est la fin d'une hospitalisation
            patient.nb_de_jours_de_suivi_post_hospit = request.form.get('nb_de_jours_de_suivi_post_hospit', 0)
            patient.nb_de_suivi_post_hospit_par_jour = request.form.get('nb_de_suivi_post_hospit_par_jour', 0)
        else:
            # Forcer à 0 si pas d’hospitalisation
            patient.nb_de_jours_de_suivi_post_hospit = 0
            patient.nb_de_suivi_post_hospit_par_jour = 0
        
        session.commit()

        return redirect(url_for('dashboard', patient=patient))

    return render_template('edit-patient.html', patient=patient)


# Supprimer un patient
@app.route('/delete-patient/<int:patient_id>', methods=["GET", "POST"])
@login_required
def deletePatient(patient_id):
    patient = session.query(Patient).filter_by(id=patient_id).first()

    if patient:
        session.delete(patient)
        session.commit()

        flash("Patient supprimé avec succès.", "success")

    else:
        flash("Patient introuvable", "error"
              )
        
    user = session.query(User).filter_by(id=current_user.id).first()
    patients = session.query(Patient).filter_by(user_id= current_user.id).all()

    return redirect(url_for('dashboard', user=user, patients=patients))


# Profil utilisateur
@app.route('/profile')
@login_required
def profile():
    user = session.query(User).filter_by(id=current_user.id).first()

    return render_template('profile.html', user=user)

# Modifier le profil utilisateur
@app.route('/edit-profile', methods=["GET", "POST"])
@login_required
def editProfile():
    user = session.query(User).filter_by(id=current_user.id).first()

    if request.method == "POST":
        surname = request.form.get('surname').upper()
        first_name = request.form.get('first_name').capitalize()
        enterprise = request.form.get('enterprise')
        email = request.form.get('email')

        # Vérifier que tous les champs sont remplis
        if not surname or not first_name or not enterprise or not email:
            flash("Tous les champs sont requis.", "error")
            return redirect(url_for('editProfile', user=user))

        # Modifier les informations dans la base de données
        user.surname = surname
        user.first_name = first_name
        user.enterprise = enterprise
        user.email = email
        
        session.commit()

        return redirect(url_for('profile', user=user))

    return render_template('edit-profile.html', user=user)


# Supprimer le compte de l'utilisateur
@app.route('/delete-profile', methods=["GET", "POST"])
@login_required
def deleteProfile():
    user = session.query(User).filter_by(id=current_user.id).first()

    if user:
        session.delete(user)
        session.commit()

        flash("Votre compte a été supprimé avec succès.", "success")

    else:
        flash("Votre compte n'a pas pu être supprimé. Contactez le support technique.", "error"
              )

    return redirect(url_for('index'))


# ===
# Run
# ===
if __name__ == '__main__':
    app.run()