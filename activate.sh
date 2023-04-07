
#!/bin/bash
set -e
# if IN_ACTIVATED_ENV is set, then we are already in the venv
if [ -n "$IN_ACTIVATED_ENV" ]; then
  return
fi
function abs_path {
  (cd "$(dirname '$1')" &>/dev/null && printf "%s/%s" "$PWD" "${1##*/}")
}
# if python is not python3, then make it
if [ "$(python --version 2>&1)" != "Python 3"* ]; then
  alias python=python3
  alias pip=pip3
fi
# if make_venv dir is not present, then make it
if [ ! -d "venv" ]; then
  python make_venv.py
fi
. $( dirname $(abs_path ${BASH_SOURCE[0]}))/venv/bin/activate
export PATH=$( dirname $(abs_path ${BASH_SOURCE[0]}))/:$PATH
export IN_ACTIVATED_ENV="1"
