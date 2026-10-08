# admin-quiz-service

> FastAPI microservice for admin operations in a quiz application. Handles admin-specific quiz management endpoints with CORS support.

## Overview

FastAPI microservice for admin operations in a quiz application. Handles admin-specific quiz management endpoints with CORS support.

## Tech Stack

Python, FastAPI

## Features

- Admin-only quiz management endpoints
- CORS configured for frontend integration
- Auto-generated OpenAPI/Swagger docs

## Getting Started

### Prerequisites

Make sure you have the tools required for this stack installed (e.g. Python 3.10+, Node.js 18+, or Android Studio).

### Installation & Usage

```bash
git clone https://github.com/<your-username>/admin-quiz-service.git
cd admin-quiz-service
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Interactive API docs: http://localhost:8000/docs
> Adjust `main:app` if your entry module is named differently.

## Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## License

Distributed under the MIT License (change as needed).

## Author

**Louai**: [GitHub](https://github.com/<your-username>)
