<<<<<<< HEAD
# README from GitHub

# Blood-bank-management
=======
# Blood Management System

A Django-based blood bank management system that helps connect blood donors with those in need. The system manages blood inventory, donor registration, and blood requests.

## Features

- User registration and authentication
- Donor registration and management
- Blood inventory tracking
- Blood request system
- Blood bank directory
- Donation history tracking
- Modern, responsive UI

## Prerequisites

- Python 3.8 or higher
- Django 4.2 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd blood-management-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Visit http://127.0.0.1:8000/ in your web browser

## Usage

1. Register as a new user
2. Log in to your account
3. Register as a donor (optional)
4. Browse available blood banks
5. Make blood requests
6. Track donation history

## Admin Interface

Access the admin interface at http://127.0.0.1:8000/admin/ to:
- Manage blood banks
- View and update blood inventory
- Process blood requests
- Manage donors and donations

## Project Structure

```
blood_management_system/
├── blood_bank/              # Main application
│   ├── migrations/         # Database migrations
│   ├── templates/         # HTML templates
│   ├── admin.py          # Admin interface configuration
│   ├── forms.py          # Form definitions
│   ├── models.py         # Database models
│   ├── urls.py           # URL configurations
│   └── views.py          # View functions
├── static/                # Static files (CSS, JS, images)
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the repository or contact the maintainers. 


=======
# README from your local project

>>>>>>> 4847fee (Initial commit)
