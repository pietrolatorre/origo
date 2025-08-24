# Origo Integration Tests

This folder contains automated integration tests for the Origo application.

## Test Scripts

### `integration-test.ps1` (Windows PowerShell)
Comprehensive integration test for Windows systems using PowerShell.

**Usage:**
```powershell
cd tests
.\integration-test.ps1
```

### `integration-test.sh` (Linux/macOS Bash)
Comprehensive integration test for Linux and macOS systems using Bash.

**Usage:**
```bash
cd tests
chmod +x integration-test.sh
./integration-test.sh
```

## What the Tests Do

The integration tests perform the following validation:

1. **Docker Configuration**: Validates docker-compose.yml syntax
2. **Service Deployment**: Builds and starts backend and frontend containers
3. **Health Checks**: Verifies backend service is responding
4. **API Testing**: Tests all REST endpoints with sample data
5. **Frontend Validation**: Confirms frontend is accessible
6. **Functional Testing**: Tests various text analysis scenarios
7. **Cleanup**: Properly stops and removes containers

## Test Output

The tests provide colored output showing:
- ✅ Successful operations in green
- ❌ Failed operations in red
- 📊 Sample analysis results
- 📋 Final test summary

## Prerequisites

- **Docker & Docker Compose** installed and running
- **Internet connection** (for downloading Docker images)
- **Available ports**: 3000 (frontend) and 8000 (backend)

## Running Tests

### Quick Test
```bash
# From project root
cd tests
.\integration-test.ps1    # Windows
./integration-test.sh     # Linux/macOS
```

### Manual Testing
If you prefer to test manually:

1. Start the application:
   ```bash
   docker-compose up --build
   ```

2. Test endpoints:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

3. Stop the application:
   ```bash
   docker-compose down
   ```

## Troubleshooting

### Common Issues

**Port conflicts:**
- Change ports in docker-compose.yml if 3000 or 8000 are in use

**Docker not running:**
- Start Docker Desktop on Windows/macOS
- Start Docker daemon on Linux

**Permission denied (Linux/macOS):**
```bash
chmod +x integration-test.sh
```

**PowerShell execution policy (Windows):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Test Results

Successful tests will show:
- All services start correctly
- Backend health check passes
- API endpoints respond with valid data
- Frontend serves the application
- Analysis functionality works end-to-end

The tests automatically clean up after completion.