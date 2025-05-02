# ECG-classification-BackEnd

1. **Clone this repository**  
   Run the following commands to clone the repo and navigate into the project directory:
   ```bash
   git clone https://github.com/ab2gbl/ECG-classification-BackEnd.git
   cd ./ECG-classification-BackEnd
   ```
2. **Create a virtual environment**
   Create a virtual environment in the project directory:

- For Windows:

```bash
python -m venv myenv
```

- For Linux:

```bash
python3 -m venv myenv
#or
python3.12 -m virtualenv env
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
pip install -r requirements.txt # --no-deps
```

4. **Place your models**
   Place your models in the following directory:
   `/acquisition/agents/models/<your model>`

- models links:
  - [TCN](https://drive.google.com/file/d/1HpYazmdleuyBTERfswcsJzbq7Vgp4MCS/view?usp=sharing)
  - [UNet](https://drive.google.com/file/d/1OgGjSDh-HdKuyGcOYPCUztTXu9U6Ld-p/view?usp=sharing)
  - [R detection](https://www.kaggle.com/models/abdessamiguebli/r-detection)
  - [Classification](https://www.kaggle.com/code/abdessamiguebli/ecg-classification/output)

5. **Run the server**
   Finally, run the servers with the following command:

```bash
python manage.py runserver
```

```bash
python manage.py runserver
```
