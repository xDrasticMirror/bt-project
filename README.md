*Note before reading: There's some stuff that's un-fully-implemented as I've kept working through the summer on the project to keep myself active while on vacation. Mostly involves swapping some dictionary bulding stuff into pydantic for faster processing and further data usage for the models. I've added an "evidences" folder for proof that the project I turned in does work.*

# TFG - Trabajo de fin de grado: Machine learning model to predict the outcome of professional e-sports League of Legends matches
## Requirements:
- Python 3 or higher
- MongoDB
- Pre-trained model
- Oracle's Elixir CSV's (downloadable and updatable through CSVUpdater.py and the frontend)
## How does it work:
### A general view:
![Description](images/basic_schema.png)

- RestAPI.py contains a Flask application (Rest API) that has includes /get_all_predictions -> which if queried with the appropiate draft data will return the winrate percentages predicted for each model (RandomForest and XGBoost)
  
