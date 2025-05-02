# Social Media Platform

A social media platform where users can create accounts, share posts, follow other users, and interact with content through likes and comments.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Installation

Follow the steps below to set up the project locally:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/social-media.git
    cd social-media
    ```

2. **Create and activate a virtual environment:**

    - **Windows:**
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

    - **macOS/Linux:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

5. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

---

## Usage

Once the project is set up, you can access the platform via your browser at `http://127.0.0.1:8000/` (default for Django's development server). Here's what you can do after logging in:

- **Register** a new account or **log in** with an existing account.
- **Customize your profile** by adding a profile picture and bio.
- **Search** for other users to connect with.
- **Create and delete posts**.
- **Like posts** from your followers or friends.
- **Follow** users to see their posts in your feed.
- **Unfollow** users if you no longer want to see their posts.
- **Explore the news feed** to see posts from followed users.
- **Log out** when you're done using the platform.

---

## Features

- **User authentication:** Registration, login, logout.
- **Profile management:** Edit profile, upload profile picture.
- **Post management:** Create and delete posts.
- **Follow/Unfollow functionality.**
- **Likes and Comments** on posts.
- **User search functionality.**
- **Responsive design** for both mobile and desktop.
  
---

## Contributing

1. **Fork the repository**.
2. **Create a feature branch** (`git checkout -b feature-name`).
3. **Commit your changes** (`git commit -am 'Add new feature'`).
4. **Push to the branch** (`git push origin feature-name`).
5. **Create a new Pull Request**.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

**Your Name**  
Email: [your.email@example.com](aaryankamalwanshi274@gmail.com)  
Project Link: [https://github.com/yourusername/social-media](https://github.com/Aaryank-47/Social-Media-Platform.git)
