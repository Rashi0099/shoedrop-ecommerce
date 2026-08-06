# Shoedrop

**Shoedrop** is a Django-based e-commerce platform designed for footwear shopping. It features a full shopping flow including user authentication, product catalogs, shopping cart, wishlist, coupon and offer management, order tracking, Razorpay payment integration, and AWS S3 media storage.

---


## 🛠️ Tech Stack

- **Backend**: Python, Django 6
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Payment Gateway**: Razorpay
- **Cloud Storage**: AWS S3 (`django-storages`, `boto3`)
- **Authentication**: Django Allauth

---

## 📦 Getting Started

### Prerequisites

Ensure you have the following installed locally:
- Python 3.10+
- PostgreSQL
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rashi0099/shoedrop-ecommerce.git
   cd shoedrop-ecommerce
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root with the required environment variables:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True

   # Database Configuration
   DB_NAME=shoedrop_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID=your_aws_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   AWS_S3_REGION_NAME=your_aws_region

   # Razorpay Configuration
   RAZORPAY_KEY_ID=your_razorpay_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret

   # Email Configuration
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**
   ```bash
   python manage.py runserver


Visit `http://127.0.0.1:8000/` in your browser to view the application.



