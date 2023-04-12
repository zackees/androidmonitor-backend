# androidmonitor-backend

#### Platform tests

[![Actions Status](../../workflows/MacOS_Tests/badge.svg)](../../actions/workflows/test_macos.yml)
[![Actions Status](../../workflows/Win_Tests/badge.svg)](../../actions/workflows/test_win.yml)
[![Actions Status](../../workflows/Ubuntu_Tests/badge.svg)](../../actions/workflows/test_ubuntu.yml)

#### Lint

[![Actions Status](../../workflows/Lint/badge.svg)](../../actions/workflows/lint.yml)


## Development

This system has been developed using the bash shell. On windows you should use git-bash, which is probably already installed if you are using git.

The backend is written in python, and uses the FastAPI framework.

To develope the software you should first run `python install_dev.py`. Then enter into
the environment with `. ./activate.sh`. YOU MUST source the activate script by using the `.` before the `./activate.sh` part, or the environment will not be activated in the current shell.

Please use the VSCode editor. To test the project use menu `Terminal` -> `Run Build Task` -> `Run Local`.

## Deployment

This project uses `docker` to deploy the application. Use `Terminal` -> `Run Build Task` -> `Build Docker Image` to build the docker image. Then use `Terminal` -> `Run Build Task` -> `Run Docker` to run the docker image locally.

For your production server you should deploy to a host like Render.com or DigitalOcean.

You'll need to set the following environmental variables:

  * `URL` - The public facing URL of the server.
  * `IS_PRODUCTION` - Set to `1` if this is a production server.
  * `DB_URL` - set this to your postgress db URL.
  * `API_KEY` - set this to your secret password that an admin will use to register users.

## Registration flow

  * backend:
    * operator adds the UID
    * one hour window opens up for registration with UID

  * client:
    * adds the UID
    * communicates with backend
    * if successful, a signed token is stored in the secure portion of the android app

  * backend:
    * UID registration window is closed
    * UID + signed token is stored in the database

  * client:
    * begins operation
    * when uploading, the token is used to grant access to the /v1/upload endpoint

## DB:

  * db identifier: androidmonitor-db
  * initial database name: androidmonitor_db
  * master username: postgres
  * password: xtoNtOAvmd0rLkFOXZvF20h4af346INA1XjR5ZzSo5
  * Account: 829547054796
  * KMS Key ID: c5a4dc13-7bc2-43b8-a5ed-1927194e7432
  * Reminder: We are on a free tier starting on 2023-Apr-12, which expires after one year

## TODO

  * [ ] UID clearing does not seem to work correctly