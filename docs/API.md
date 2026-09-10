# API Documentation: NIRIKSHAN (v1)

## Base URL
`/api/v1`

## Endpoints

### Projects
- `GET /projects`
  - Lists projects with pagination and filtering.
  - Query Params: `q`, `data_source`, `completion_status`, `risk_level`, `longitude`, `latitude`, `radius_m`.
- `GET /projects/{id}`
  - Returns full project details, including evidence and latest risk assessment.
- `POST /projects`
  - Creates a new project.

### Risks
- `GET /risks`
  - Lists all risk assessments across the system.
- `GET /projects/{id}/risks`
  - Returns the risk history for a specific project.
- `POST /risks/assess/{id}`
  - Triggers the Risk Engine to perform a fresh assessment of the project.
- `POST /risks/{assessment_id}/review`
  - Updates the verification status (e.g., `HUMAN_VERIFIED`) and adds reviewer remarks.

### Entities
- `GET /contractors`
  - Lists all registered contractors and their award counts.
- `GET /tenders`
  - Lists all recorded tenders.

### Health
- `GET /health`
  - Checks application and database connectivity.

## Error Responses
The API uses consistent error formats:
```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human readable explanation",
    "context": {}
  }
}
```
