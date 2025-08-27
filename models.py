from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship
from zoneinfo import ZoneInfo

Base = declarative_base()

# Utilisateurs
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String, index=True)
    first_name = Column(String, index=True)
    enterprise = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

        # Un utilisateur a plusieurs patients
    patients = relationship("Patient", back_populates="owner_user", cascade="all, delete-orphan")


# Patients
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True, index=True)
    ipp = Column(String, index=True)
    surname = Column(String, index=True)
    first_name = Column(String, index=True)
    day_of_birthday = Column(String, index=True)
    month_of_birthday = Column(String, index=True)
    year_of_birthday = Column(String, index=True)
    personnage = Column(String)
    end_of_hospitalisation = Column(Boolean)
    nb_de_jours_de_suivi_post_hospit = Column(Integer)
    nb_de_suivi_post_hospit_par_jour = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Paris")))

    # Clé étrangère vers l'utilisateur propriétaire
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relation vers l'utilisateur
    owner_user = relationship("User", back_populates="patients")

    # Un patient a plusieurs suivi
    suivis = relationship("Suivi", back_populates="owner_suivi", cascade="all, delete-orphan")

    # Un patient a plusieurs validations d'item
    validations = relationship("Validation", back_populates="owner_validation", cascade="all, delete-orphan")

    @property
    def birthday(self):
        return f"{self.day_of_birthday}/{self.month_of_birthday}/{self.year_of_birthday}"

# Suivis
class Suivi(Base):
    __tablename__ = 'suivis'

    id = Column(Integer, primary_key=True, index=True)
    type_de_suivi = Column(String)
    evaluation = Column(String)
    soin_souhaite = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Europe/Paris")))

    # Clé étrangère vers le patient propriétaire
    patient_id = Column(Integer, ForeignKey("patients.id"))

    # Relation vers le patient
    owner_suivi = relationship("Patient", back_populates="suivis")


# Validations
class Validation(Base):
    __tablename__ = "validations"

    id = Column(Integer, primary_key=True, index=True)
    validation_presentation = Column(Boolean)
    validation_maison = Column(Boolean)
    presentationItem = Column(Boolean)
    besoinItem = Column(Boolean)
    maisonItem = Column(Boolean)
    testItem = Column(Boolean)

    # Clé étrangère vers le patient propriétaire
    patient_id = Column(Integer, ForeignKey("patients.id"))

    # Relation vers le patient
    owner_validation = relationship("Patient", back_populates="validations")

