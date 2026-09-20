### Installation

#### 1. Clone the Repository

    git clone https://github.com/khushikhushali6-svg/branded-link-hub.git
    cd branded-link-hub

#### 2. Create a Virtual Environment

Windows:

    python -m venv venv

Activate the environment:

    venv\Scripts\activate

#### 3. Install Dependencies

    pip install -r requirements.txt

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

    SECRET_KEY=your-secret-key
    JWT_SECRET_KEY=your-jwt-secret-key
    DATABASE_URL=sqlite:///branded_link_hub.db

Do not commit the `.env` file to GitHub.

#### 5. Run the Application

    python run.py

The application will be available at:

    http://127.0.0.1:5000

---

## Demo Flow

The recommended demonstration flow is:

1. Open the LinkHub landing page.
2. Register a user.
3. Complete the verification flow.
4. Log in.
5. Create a short link.
6. Create a custom slug.
7. Copy the generated short URL.
8. Open the public short URL.
9. Generate a QR code.
10. Open link analytics.
11. Customize the profile.
12. Upload an avatar.
13. Add social links.
14. Change the profile theme.
15. Open the public bio profile.
16. Verify active links and visible social links.
17. Log out.
18. Verify dashboard protection.
19. Verify session-expiry handling.

---

## Validation & Error Handling

The application performs validation for:

- Required fields
- Email format
- Username format
- Password length
- HTTP and HTTPS URLs
- Custom slug format
- Duplicate custom slugs
- Link title length
- Avatar file extension
- Avatar file size
- Social link fields
- Authentication state

API errors return appropriate HTTP status codes with JSON error messages.

---

## Security Considerations

The application implements:

- Password hashing using Werkzeug
- JWT authentication
- HttpOnly authentication cookies
- CSRF protection
- Protected dashboard routes
- Protected API endpoints
- Refresh-token rotation
- Rate limiting
- Hashed IP storage for analytics
- Environment-based secret configuration
- Server-side input validation

For HTTPS deployment, secure cookies should be enabled.

---

## Local Development Notes

Generated short URLs and QR codes use the current application host.

When running locally at:

    http://127.0.0.1:5000

the generated short URL is intended for local development. To access the application from another device, it must be exposed through a reachable network host.

---

## Current Limitations

The following parts are simplified for the assessment implementation:

- Email verification and password-reset emails use application-generated verification/reset links instead of an external email delivery service.
- Refresh-token tracking currently uses an in-memory store.
- SQLite is used as the development database.
- The default rate-limiter storage is suitable for development; production deployments should use shared persistent storage such as Redis.
- HTTPS deployment should enable secure cookies.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask application secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | Database connection string |

---

## GitHub Repository

    https://github.com/khushikhushali6-svg/branded-link-hub

---

## Project Status

The core assessment requirements have been implemented, including authentication, branded short links, public redirection, QR code generation, link analytics, profile customization, social links, public bio pages, validation, security controls, and responsive frontend functionality.

The project demonstrates backend API development, database integration, authentication, business logic, frontend integration, validation, security, and technical documentation.