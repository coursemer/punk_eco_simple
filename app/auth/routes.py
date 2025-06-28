"""
Routes d'authentification pour l'application Punk Eco.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from ..models.user import User
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion des utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Connexion réussie!', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnecte l'utilisateur actuel."""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Gère l'inscription des nouveaux utilisateurs."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation des données
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=email).first():
            flash('Un compte avec cet email existe déjà.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Vérifier si le nom d'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Créer un nouvel utilisateur
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        
        flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
