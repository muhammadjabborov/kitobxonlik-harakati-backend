# API Reference

This file documents the mounted API endpoints in this Django project. Paths are case-sensitive and include trailing slashes exactly as shown.

## Base

- API base prefix: `/api/v1/`
- JSON renderer: all API responses are JSON.
- Auth header for protected endpoints: `Authorization: Bearer <access_token>`
- JWT access token lifetime: 1 day.
- JWT refresh token lifetime: 30 days.
- Default paginated list shape:

```json
{
  "count": 123,
  "next": "http://example.com/api/path/?limit=10&offset=10",
  "previous": null,
  "results": []
}
```

Paginated endpoints support `limit` and `offset`. The default page size is `10`.

## Shared Schemas

### Region

```json
{
  "id": 1,
  "name": "Toshkent shahri",
  "soato": "1726",
  "level": 0,
  "parent": null
}
```

`parent` is either `null` or another nested `Region`.

### User

```json
{
  "id": 1,
  "full_name": "User Name",
  "phone_number": "+998901234567",
  "birth_date": "2010-01-31",
  "grade": "6",
  "region": 1,
  "identity_type": "passport",
  "identity_number": "AA1234567"
}
```

In profile responses, `region` is a nested `Region` object instead of an id.

### Book Short

```json
{
  "id": 1,
  "title": "Book title",
  "slug": "book-title",
  "image": "https://example.com/media/books/covers/..."
}
```

### Author

```json
{
  "id": 1,
  "name": "Author name"
}
```

### Genre

```json
{
  "id": 1,
  "title": "Genre title"
}
```

## Auth Flow

### Existing User Login Flow

1. `POST /api/v1/users/auth/CheckPhoneNumber/`
2. If `registered=true`, the response includes a `session`.
3. `POST /api/v1/users/auth/Login/` with `phone_number`, `session`, and OTP `code`.
4. Store the returned `access` token for protected endpoints.

`POST /api/v1/users/auth/SendAuthVerificationCode/` can also send an auth OTP and return a new `session`.

### New User Registration Flow

1. `POST /api/v1/users/auth/Register/` with user form data.
2. The backend caches the form data for 10 minutes and returns a `session`.
3. `POST /api/v1/users/auth/CheckRegisterOTP/` with `session` and OTP `code`.
4. The backend creates the user and returns JWT tokens plus the user object.

Registration and auth OTP sending are rate-limited to 3 sends per phone number per 120 seconds.

Allowed `grade` values:

```text
1_5, 6, 7, 8, 9, 10, 11
```

Allowed `identity_type` values:

```text
passport, metric
```

## Common

### GET `/api/v1/common/RegionList/`

Auth: public

Query params:

- `parent`: integer region id. Returns children of the given parent.
- `is_region`: boolean. Use `true` to return top-level regions.
- `search`: string. Searches by region name.

At least one of `parent` or `is_region` is required.

Response: non-paginated array of `Region`.

```json
[
  {
    "id": 1,
    "name": "Toshkent shahri",
    "soato": "1726",
    "level": 0,
    "parent": null
  }
]
```

### GET `/api/v1/common/SchoolList/`

Auth: public

Query params:

- `district_id`: integer. Filters schools by district.
- `region_id`: integer. Filters schools by parent region.

If no query params are provided, all schools are returned.

Response: non-paginated array.

```json
[
  {
    "id": 1,
    "name": "School name"
  }
]
```

### GET `/api/v1/common/health-check/redis/`

Auth: public

Success response:

```json
{
  "status": "success"
}
```

Error response:

```json
{
  "status": "error",
  "message": "Redis server is not working."
}
```

### GET `/api/v1/common/health-check/celery/`

Auth: public

Success response:

```json
{
  "status": "success",
  "workers": []
}
```

Error responses:

```json
{
  "status": "error",
  "message": "No Celery workers responded."
}
```

```json
{
  "status": "error",
  "message": "Celery OperationalError occurred."
}
```

## Users

### POST `/api/v1/users/auth/CheckPhoneNumber/`

Auth: public

Request:

```json
{
  "phone_number": "+998901234567"
}
```

If the phone number is not registered:

```json
{
  "registered": false
}
```

If the phone number is registered, the backend sends an OTP:

```json
{
  "registered": true,
  "session": "abc123session"
}
```

### POST `/api/v1/users/auth/SendAuthVerificationCode/`

Auth: public

Request:

```json
{
  "phone_number": "+998901234567"
}
```

Response:

```json
{
  "session": "abc123session"
}
```

### POST `/api/v1/users/auth/Login/`

Auth: public

Request:

```json
{
  "phone_number": "+998901234567",
  "code": "7777",
  "session": "abc123session"
}
```

Response:

```json
{
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token",
  "user": {
    "id": 1,
    "full_name": "User Name",
    "phone_number": "+998901234567",
    "birth_date": "2010-01-31",
    "grade": "6",
    "region": 1,
    "identity_type": "passport",
    "identity_number": "AA1234567"
  }
}
```

### POST `/api/v1/users/auth/Register/`

Auth: public

Request:

```json
{
  "phone_number": "+998901234567",
  "full_name": "User Name",
  "birth_date": "2010-01-31",
  "grade": "6",
  "region": 1,
  "identity_type": "passport",
  "identity_number": "AA1234567"
}
```

Optional request fields:

- `birth_date`
- `grade`
- `region`
- `identity_type`
- `identity_number`

Response:

```json
{
  "session": "abc123session"
}
```

### POST `/api/v1/users/auth/CheckRegisterOTP/`

Auth: public

Request:

```json
{
  "session": "abc123session",
  "code": "7777"
}
```

Response status: `201 Created`

Response:

```json
{
  "refresh": "jwt-refresh-token",
  "access": "jwt-access-token",
  "user": {
    "id": 1,
    "full_name": "User Name",
    "phone_number": "+998901234567",
    "birth_date": "2010-01-31",
    "grade": "6",
    "region": 1,
    "identity_type": "passport",
    "identity_number": "AA1234567"
  }
}
```

### GET `/api/v1/users/profile/GetProfile/`

Auth: required

Response:

```json
{
  "id": 1,
  "full_name": "User Name",
  "phone_number": "+998901234567",
  "birth_date": "2010-01-31",
  "grade": "6",
  "region": {
    "id": 1,
    "name": "Toshkent shahri",
    "soato": "1726",
    "level": 0,
    "parent": null
  },
  "identity_type": "passport",
  "identity_number": "AA1234567"
}
```

## Books

### GET `/api/v1/book/BookList/`

Auth: public

Pagination: yes

Query params:

- `search`: string. Searches `title` and `slug`.
- `limit`: integer.
- `offset`: integer.

Code-level note: Swagger declares `date` and `grades`, but the current `BookListFilter` does not apply those filters.

Response item:

```json
{
  "id": 1,
  "title": "Book title",
  "slug": "book-title",
  "image": "https://example.com/media/books/covers/...",
  "authors": [
    {
      "id": 1,
      "name": "Author name"
    }
  ],
  "genres": [
    {
      "id": 1,
      "title": "Genre title"
    }
  ]
}
```

### GET `/api/v1/book/HomeBookList/`

Auth: public

Pagination: no

Returns the first 4 active books ordered by `id`. The view is cached for 1 hour.

Response: non-paginated array of the same item shape as `BookList`.

### GET `/api/v1/book/BookDetail/<book_identifier>/`

Auth: public

`book_identifier` can be a numeric book id or a slug.

Response:

```json
{
  "id": 1,
  "title": "Book title",
  "description": "Book description",
  "image": "https://example.com/media/books/covers/...",
  "slug": "book-title",
  "genres": [
    {
      "id": 1,
      "title": "Genre title"
    }
  ],
  "authors": [
    {
      "id": 1,
      "name": "Author name"
    }
  ],
  "audio_duration": 3600,
  "audio_book_count": 12,
  "epub_file": "https://example.com/media/books/epub/..."
}
```

### GET `/api/v1/book/AudioBookList/<book_identifier>/`

Auth: public

`book_identifier` can be a numeric book id or a slug.

Response:

```json
{
  "book_info": {
    "id": 1,
    "title": "Book title",
    "slug": "book-title",
    "image": "https://example.com/media/books/covers/..."
  },
  "audio_files": [
    {
      "id": 1,
      "title": "Chapter 1",
      "file": "https://example.com/media/books/audio/...",
      "duration": 123.45,
      "order": 1
    }
  ]
}
```

### GET `/api/v1/book/AudioBookDetail/<pk>/`

Auth: public

Response:

```json
{
  "id": 1,
  "book_info": {
    "id": 1,
    "title": "Book title",
    "slug": "book-title",
    "image": "https://example.com/media/books/covers/..."
  },
  "title": "Chapter 1",
  "file": "https://example.com/media/books/audio/...",
  "duration": 123.45,
  "order": 1
}
```

## Plan To Read

All Plan To Read endpoints require auth.

### GET `/api/v1/book/PlanToReadList/`

Pagination: yes

Returns the authenticated user's saved books.

Response item:

```json
{
  "id": 1,
  "book": {
    "id": 1,
    "title": "Book title",
    "slug": "book-title",
    "image": "https://example.com/media/books/covers/...",
    "authors": [
      {
        "id": 1,
        "name": "Author name"
      }
    ]
  }
}
```

### POST `/api/v1/book/PlanToReadCreate/`

Request:

```json
{
  "book": 1
}
```

Response status: `201 Created`

Response:

```json
{
  "id": 1,
  "book": 1
}
```

If the same user already saved the same book, the existing row is returned instead of creating a duplicate.

### DELETE `/api/v1/book/PlanToReadDelete/<book_id>/`

Deletes the authenticated user's Plan To Read row by book id.

Success response status: `204 No Content`

## Assessment Flow

1. `GET /api/v1/assessment/MonthlyAssessmentList/`
2. If an assessment has `status=available`, call `POST /api/v1/assessment/StartAssessment/<assessment_id>/`.
3. If an assessment has `status=in_progress`, call `GET /api/v1/assessment/ReenterAssessment/<attempt_id>/`.
4. Submit answers with `POST /api/v1/assessment/SubmitAssessment/<attempt_id>/`.

All assessment endpoints require auth and use the authenticated user's `grade`.

Question types:

```text
multiple_choice, short_answer
```

Assessment statuses:

```text
completed, in_progress, available, locked
```

### GET `/api/v1/assessment/MonthlyAssessmentList/`

Auth: required

Pagination: no

Response:

```json
[
  {
    "id": 1,
    "grade": "6",
    "month_start": "2026-06-01",
    "start_time": "2026-06-01T00:00:00+05:00",
    "end_time": "2026-06-30T23:59:59+05:00",
    "time_limit": 1800,
    "attempt": {
      "id": 1,
      "total_score": "80.00",
      "spent_time_ms": 1200000
    },
    "status": "completed"
  }
]
```

`attempt` is `null` if the user has not started that assessment.

### POST `/api/v1/assessment/StartAssessment/<assessment_id>/`

Auth: required

Request: no body

Creates one attempt for the authenticated user. The assessment must match the user's grade, belong to the active season, and have a `month_start` date that is not in the future.

Response status: `201 Created`

Response:

```json
{
  "id": 1,
  "started_at": "2026-06-24T10:00:00+05:00",
  "time_limit": 1800,
  "user_questions": [
    {
      "user_question_id": 10,
      "question_type": "multiple_choice",
      "question_text": "Question text",
      "question_options": [
        {
          "id": 100,
          "option_text": "Option A"
        }
      ]
    }
  ]
}
```

For `short_answer` questions, `question_options` can be an empty array.

### GET `/api/v1/assessment/ReenterAssessment/<attempt_id>/`

Auth: required

Returns an unfinished attempt for the authenticated user.

Response: same shape as `StartAssessment`.

### POST `/api/v1/assessment/SubmitAssessment/<attempt_id>/`

Auth: required

The attempt must belong to the authenticated user and must not already be completed.

Request:

```json
{
  "answers": [
    {
      "user_question_id": 10,
      "selected_option_id": 100
    },
    {
      "user_question_id": 11,
      "submitted_answer": "Text answer"
    }
  ]
}
```

For `multiple_choice`, send `selected_option_id`.

For `short_answer`, send `submitted_answer`.

Response:

```json
{
  "total_score": "80.00",
  "correct_count": 8,
  "total_count": 10
}
```

## Schema And API Docs

These endpoints are mounted outside `/api/v1/`:

- `GET /swagger.json`
- `GET /swagger.yaml`
- `GET /swagger/`
- `GET /redoc/`

## Unmounted API View Classes

The codebase contains `DistrictListView` and `NeighborhoodListView`, but they are not included in `apps/common/urls.py`, so they are not currently reachable through mounted URLs.

## Common Error Shapes

Validation errors usually return field-keyed objects:

```json
{
  "field_name": [
    "Error message"
  ]
}
```

Some custom validation errors return object values:

```json
{
  "code": "Wrong code!"
}
```

Protected endpoints return `401 Unauthorized` when the access token is missing or invalid. Missing resources return `404 Not Found`.
