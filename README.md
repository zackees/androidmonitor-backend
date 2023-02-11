# androidmonitor-backend

#### Platform tests

[![Actions Status](../../workflows/MacOS_Tests/badge.svg)](../../actions/workflows/test_macos.yml)
[![Actions Status](../../workflows/Win_Tests/badge.svg)](../../actions/workflows/test_win.yml)
[![Actions Status](../../workflows/Ubuntu_Tests/badge.svg)](../../actions/workflows/test_ubuntu.yml)

#### Lint

[![Actions Status](../../workflows/Lint/badge.svg)](../../actions/workflows/lint.yml)


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