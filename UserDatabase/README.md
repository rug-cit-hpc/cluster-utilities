# User Database
## Setup
- Build and activate a Python 3 virtual environment:
```bash
module purge
module load Python/3.6.4-foss-2018a
python3 -m venv $HOME/.envs/UserDatabase
```
- Upgrade pip and install the required packages:
```bash
source $HOME/.envs/UserDatabase/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```
## Running
- Make sure that the `LDAP.conf` file is in this folder;
- Run the bash script:
```bash
./updateDB.sh
```