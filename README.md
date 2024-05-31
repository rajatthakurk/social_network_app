# Social Network API

## Installation

Clone the repository:

   ```bash
   git clone https://github.com/rajatthakurk/social_network_app.git
   cd social_network
```
Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```
Create a superuser (optional, for accessing the admin panel):

```bash
python manage.py createsuperuser
```
Run the development server:

```bash
python manage.py runserver
```
Docker
To run the application using Docker Build and run the Docker containers:

```bash
docker-compose up --build
Access the application at http://localhost:8000.
```
## API Endpoints
* POST /api/signup/: User signup
* POST /api/login/: User login
* GET /api/search/?q=<keyword>: Search users by email or name (case-insensitive)
* POST /api/friend-request/: Send a friend request
* POST /api/friend-request/<int:request_id>/: Manage (accept/reject) a friend request
* GET /api/friends/: List friends
* GET /api/pending-requests/: List pending friend requests
