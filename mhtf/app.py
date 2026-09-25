import json
import os
from datetime import datetime
from functools import wraps

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Bitte zuerst anmelden. / Please sign in first."

TEXT = {
    "de": {"dashboard":"Übersicht","plans":"Medikationspläne","rfid":"RFID-Chips","logs":"Protokoll","logout":"Abmelden","login":"Anmelden","save":"Speichern","new_plan":"Neuen Medikationsplan","new_rfid":"RFID-Chip hinzufügen","welcome":"Willkommen zurück","system":"Systemstatus","active":"Aktiv","inactive":"Inaktiv","edit":"Bearbeiten","toggle":"Status ändern","delete":"Löschen","patient":"Patient","medication":"Medikament","strength":"Stärke","dosage":"Dosierung","time":"Uhrzeit","weekdays":"Wochentage","amount":"Anzahl","actions":"Aktionen"},
    "en": {"dashboard":"Dashboard","plans":"Medication plans","rfid":"RFID tags","logs":"Activity log","logout":"Sign out","login":"Sign in","save":"Save","new_plan":"New medication plan","new_rfid":"Add RFID tag","welcome":"Welcome back","system":"System status","active":"Active","inactive":"Inactive","edit":"Edit","toggle":"Change status","delete":"Delete","patient":"Patient","medication":"Medication","strength":"Strength","dosage":"Dosage","time":"Time","weekdays":"Weekdays","amount":"Quantity","actions":"Actions"}
}

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(5), nullable=False, default="de")
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    @property
    def is_active(self): return bool(self.active)

class MedicationPlan(db.Model):
    __tablename__ = "medication_plans"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    patient_name = db.Column(db.String(120), nullable=False)
    medication_name = db.Column(db.String(120), nullable=False)
    strength = db.Column(db.String(50), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    intake_time = db.Column(db.Time, nullable=False)
    weekdays = db.Column(db.String(50), nullable=False)
    medication_amount = db.Column(db.Integer, nullable=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class RFIDCard(db.Model):
    __tablename__ = "rfid_cards"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    label = db.Column(db.String(120), nullable=False)
    person_name = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventLog(db.Model):
    __tablename__ = "event_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    result = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id): return db.session.get(User, int(user_id))

def t(key):
    lang=session.get("lang", "de")
    return TEXT.get(lang, TEXT["de"]).get(key, key)

@app.context_processor
def inject_globals(): return {"t":t, "lang":session.get("lang","de")}

def log(action, entity_type=None, entity_id=None, result="success"):
    db.session.add(EventLog(user_id=current_user.id if current_user.is_authenticated else None, action=action, entity_type=entity_type, entity_id=entity_id, result=result))
    db.session.commit()

def owner_or_admin(plan): return current_user.role == "admin" or plan.user_id == current_user.id

mqtt_client=None
mqtt_online=False
try:
    mqtt_client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.connect(os.getenv("MQTT_HOST","127.0.0.1"), int(os.getenv("MQTT_PORT","1883")), 60)
    mqtt_client.loop_start(); mqtt_online=True
except Exception as exc: print(f"MQTT nicht erreichbar: {exc}")

def publish(topic, payload):
    if mqtt_client:
        try: mqtt_client.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1)
        except Exception as exc: print(f"MQTT publish fehlgeschlagen: {exc}")

@app.route("/language/<language>")
def language(language):
    if language in ("de","en"): session["lang"]=language
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("dashboard"))
    if request.method=="POST":
        user=User.query.filter_by(username=request.form.get("username","").strip()).first()
        if user and user.active and check_password_hash(user.password_hash, request.form.get("password","")):
            login_user(user); session["lang"]=user.language; log("login","user",user.id)
            return redirect(url_for("dashboard"))
        flash("Anmeldung fehlgeschlagen / Sign-in failed", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    log("logout","user",current_user.id); logout_user(); return redirect(url_for("login"))

@app.route("/")
@login_required
def dashboard():
    plans_q=MedicationPlan.query if current_user.role=="admin" else MedicationPlan.query.filter_by(user_id=current_user.id)
    return render_template("dashboard.html", plan_count=plans_q.count(), active_count=plans_q.filter_by(active=True).count(), rfid_count=RFIDCard.query.count(), recent_logs=EventLog.query.order_by(EventLog.created_at.desc()).limit(6).all(), mqtt_online=mqtt_online)

@app.route("/plans")
@login_required
def plans():
    q=MedicationPlan.query if current_user.role=="admin" else MedicationPlan.query.filter_by(user_id=current_user.id)
    return render_template("plans.html", plans=q.order_by(MedicationPlan.intake_time).all())

@app.route("/plans/new", methods=["GET","POST"])
@login_required
def plan_new():
    if request.method=="POST":
        days=",".join(request.form.getlist("weekdays"))
        if not days: flash("Mindestens einen Wochentag auswählen.","error"); return render_template("plan_form.html", plan=None)
        plan=MedicationPlan(user_id=current_user.id, patient_name=request.form["patient_name"].strip(), medication_name=request.form["medication_name"].strip(), strength=request.form["strength"].strip(), dosage=request.form["dosage"].strip(), intake_time=request.form["intake_time"], weekdays=days, medication_amount=max(0,int(request.form.get("medication_amount",0))), active=request.form.get("active")=="on")
        db.session.add(plan); db.session.commit(); log("medication plan created","medication_plan",plan.id)
        publish("mhtf/medication/created", {"event":"medication_created","patient":plan.patient_name,"medication":plan.medication_name,"plan_id":plan.id})
        flash("Medikationsplan gespeichert.","success"); return redirect(url_for("plans"))
    return render_template("plan_form.html", plan=None)

@app.route("/plans/<int:plan_id>/edit", methods=["GET","POST"])
@login_required
def plan_edit(plan_id):
    plan=db.get_or_404(MedicationPlan,plan_id)
    if not owner_or_admin(plan): return ("Forbidden",403)
    if request.method=="POST":
        days=",".join(request.form.getlist("weekdays"))
        plan.patient_name=request.form["patient_name"].strip(); plan.medication_name=request.form["medication_name"].strip(); plan.strength=request.form["strength"].strip(); plan.dosage=request.form["dosage"].strip(); plan.intake_time=request.form["intake_time"]; plan.weekdays=days; plan.medication_amount=max(0,int(request.form.get("medication_amount",0))); plan.active=request.form.get("active")=="on"
        db.session.commit(); log("medication plan updated","medication_plan",plan.id); flash("Plan aktualisiert.","success"); return redirect(url_for("plans"))
    return render_template("plan_form.html", plan=plan)

@app.post("/plans/<int:plan_id>/toggle")
@login_required
def plan_toggle(plan_id):
    plan=db.get_or_404(MedicationPlan,plan_id)
    if not owner_or_admin(plan): return ("Forbidden",403)
    plan.active=not plan.active; db.session.commit(); log("medication plan toggled","medication_plan",plan.id); return redirect(url_for("plans"))

@app.post("/plans/<int:plan_id>/delete")
@login_required
def plan_delete(plan_id):
    plan=db.get_or_404(MedicationPlan,plan_id)
    if not owner_or_admin(plan): return ("Forbidden",403)
    db.session.delete(plan); db.session.commit(); log("medication plan deleted","medication_plan",plan_id); return redirect(url_for("plans"))

@app.route("/rfid", methods=["GET","POST"])
@login_required
def rfid():
    if request.method=="POST":
        card=RFIDCard(uid=request.form["uid"].strip().upper(), label=request.form["label"].strip(), person_name=request.form["person_name"].strip(), active=request.form.get("active")=="on")
        try:
            db.session.add(card); db.session.commit(); log("rfid created","rfid_card",card.id); publish("mhtf/rfid/created", {"uid":card.uid,"person":card.person_name}); flash("RFID-Chip gespeichert.","success")
        except IntegrityError:
            db.session.rollback(); flash("UID existiert bereits / UID already exists","error")
        return redirect(url_for("rfid"))
    return render_template("rfid.html", cards=RFIDCard.query.order_by(RFIDCard.created_at.desc()).all())

@app.post("/rfid/<int:card_id>/toggle")
@login_required
def rfid_toggle(card_id):
    card=db.get_or_404(RFIDCard,card_id); card.active=not card.active; db.session.commit(); log("rfid toggled","rfid_card",card.id); return redirect(url_for("rfid"))

@app.post("/rfid/<int:card_id>/delete")
@login_required
def rfid_delete(card_id):
    card=db.get_or_404(RFIDCard,card_id); db.session.delete(card); db.session.commit(); log("rfid deleted","rfid_card",card_id); return redirect(url_for("rfid"))

@app.route("/logs")
@login_required
def logs(): return render_template("logs.html", logs=EventLog.query.order_by(EventLog.created_at.desc()).limit(150).all())

if __name__=="__main__": app.run(host="0.0.0.0",port=5000,debug=False)
