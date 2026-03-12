# Android Enterprise Admin Console

Small Flask web app for admin control of Android Enterprise operations through a smart dashboard UI.

## Features

- One-click policy deployment from the browser
- Device sync, lock, and wipe actions backed by Python handlers
- Admin dashboard with summary cards, policy list, managed device table, and activity history
- Service layer ready to replace mock handlers with real Android Enterprise API code

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Integration point

Real Android Enterprise logic should be added in `services/android_enterprise.py` inside `_run_python_job()`. That method is where you can:

- call your existing Python scripts with `subprocess`
- add direct Google Android Management API calls
- inject credentials and tenant-specific configuration
