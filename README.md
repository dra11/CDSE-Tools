# CDSE-Tools

Copernicus Data Space Ecosystem Tools: The python script 'cdse_search_n_download.py' searches and downloads Earth Observation data from Copernicus Data Space Ecosystem (CDSE)

Features: 

  - Enabled_for_Parallel_Downloading,  
  - Lists_all_query_results,  
  - User_choice_for_number_of_product_downloads_during_runtime.


Before executing the python script:

  - One must have a valid CDSE User Account. If not, go here - https://dataspace.copernicus.eu/  
  - Also read this for eligible quotas: https://documentation.dataspace.copernicus.eu/Quotas.html#copernicus-general-users
  
  - Create your environment variables for your valid CDSE account credentials first by running the below two lines of code in bash:
  
        export CDSE_USER="enter_your_username"  
        export CDSE_PASS="enter_your_password"
