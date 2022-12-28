# Yatube_social_net)
This is a project of a simple social network where users can create, edit and comment on posts, subscribe to each other. View the latest posts of all users on the main page, or go to the subscriptions page and see posts only by the authors you like. Individual author profile pages and a detailed view of a particular post are also available.

## Local setup
Clone repository and go to directory "yatube_social_net"

git clone https://github.com/VitaliiLuki/yatube_social_net.git
cd yatube_social_net/

Create and activate virtual environment

python3 -m venv venv 
source venv/bin/activate

Install all dependencies from requirements.txt

pip install --upgrade pip
python3 -m pip install -r requirements.txt

Go to directory with a manage.py, make migrations and run server

cd yatube
python3 manage.py migrate
python3 manage.py runserver

Endpoints:

- Registration, entering to website and password reset:

    1. To registrate a new user:

        /auth/signup/

    2. To log in to website:

        /auth/signin/

    3. To change a password:

        /auth/password_change/

    4. To reset a passwoed:

        /auth/password_reset/

- User activities on a website:

    1. To create a new post:

        /create/

    2. To edit/delete/comment the post:

        /posts/<int:post_id>/edit/
        /posts/<int:post_id>/delete/
        /posts/<int:post_id>/comment/

    3. Watch all user's posts(main page):

        /

    4. Watch posts of your favorite authors:

        /follow/

    5. Go to author's profile:

        /profile/<str:username>/

    6. To subscribe/unsubscribe to/from the author:

        /profile/<str:username>/follow/
        /profile/<str:username>/unfollow/

    7. Watch posts which related to certain group:

        /group/<slug:slug>/

- Admin page:

    /admin/

- Information about person who created website:

    /about/

Tech stack

Python, Django, HTML
