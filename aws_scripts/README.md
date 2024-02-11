# AWS scripts with utils

Few useful python scripts to use over AWS

### Prepare environment
> python -m venv venv  
> source venv/bin/activate  
> pip install -r requirements.txt  


### Generate AWS config file
The script expects to have a config file `accounts.yml` with the list of accounts to work with.
See `accounts-demo.yml` as an example if you want to create manually.   
If the file is not found, it will create one automatically for you. You may need to adapt that file to your needs

