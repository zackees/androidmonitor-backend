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

  * Render.com Postgres:
    * postgres://androidmonitor_backend_db_user:bNft2nTH4UZ2Uk7KNBtwowdNNm9wGIqU@dpg-cfv8nit269v0ptk5cnlg-a.oregon-postgres.render.com/androidmonitor_backend_db

## TODO

  * [ ] UID clearing does not seem to work correctly