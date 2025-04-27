# ECG-classification-BackEnd

1. **Clone this repository**  
   Run the following commands to clone the repo and navigate into the project directory:
   ```bash
   git clone https://github.com/ab2gbl/ECG-classification-BackEnd.git
   cd ./ECG-classification-BackEnd
   ```
 2.  **Create a virtual environment**
Create a virtual environment in the project directory:

- For Windows:
```bash
python -m venv myenv
```
- For Linux:
```bash
    python3 -m venv myenv
```
3. **Activate the virtual environment**
Activate the virtual environment to start using it:
- For Windows:
```bash
myenv\Scripts\activate
```
- For Linux:
```bash
    source myenv/bin/activate
```
3. **Install the required dependencies**
Install the necessary Python packages listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```
4. **Place your models**
Place your models in the following directory:
`/acquisition/agents/models/<your model>`

5. **Run the server**
Finally, run the server with the following command:
```bash
python manage.py runserver
```
