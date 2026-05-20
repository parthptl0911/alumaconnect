# AlumConnect

A comprehensive Django-based platform connecting alumni and students through mentorship, job opportunities, events, fundraising, and community engagement.

## Features

- **User Management**: Role-based user system for students and alumni
- **Mentorship Program**: Connect students with experienced alumni mentors
- **Job Board**: Post and apply for job opportunities
- **Events**: Create and manage alumni and student events
- **Fundraising**: Campaign management with Razorpay payment integration
- **Stories**: Share and read alumni success stories
- **Chat System**: Real-time messaging between users
- **Alumni Directory**: Browse and connect with alumni network

## Tech Stack

- **Backend**: Django 3.x/4.x
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Payment Gateway**: Razorpay
- **Authentication**: Django built-in auth system

## Project Structure

```
almaconnect/          # Main Django project settings
apps/                 # Django applications
  ├── accounts/       # User authentication & profiles
  ├── alumni/         # Alumni management
  ├── chat/           # Messaging system
  ├── events/         # Events management
  ├── fundraising/    # Fundraising campaigns
  ├── jobs/           # Job postings & applications
  ├── mentorship/     # Mentorship requests & connections
  └── stories/        # Alumni stories
templates/            # HTML templates
static/               # CSS, JavaScript, images
media/                # User uploads (avatars, resumes, etc.)
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/parthptl0911/alumaconnect.git
cd alumaconnect
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Configuration

Create a `.env` file in the root directory with:
```
RAZORPAY_KEY_ID=your_key_here
RAZORPAY_KEY_SECRET=your_secret_here
SECRET_KEY=your_django_secret_key
DEBUG=True
```

## Usage

### Admin Panel
Access Django admin at `/admin` using superuser credentials.

### User Registration
Users can register as students or alumni through the registration page.

### Mentorship Requests
Students can browse available mentors and send mentorship requests.

### Job Postings
Alumni can post jobs and students can apply with resumes.

### Fundraising Campaigns
Create fundraising campaigns with Razorpay payment integration.

## Running Tests

```bash
python run_tests.py
```

Or use Django's test runner:
```bash
python manage.py test
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Contact

For questions or support, please contact: parthptl0911@gmail.com

---

**Made with ❤️ for the alumni community**