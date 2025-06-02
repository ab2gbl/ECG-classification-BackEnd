# ECG-classification-BackEnd

## 1. Project install

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
  - [UNet](https://www.kaggle.com/models/abdessamiguebli/unet-model-for-ecg-mask-detection/pyTorch/default)
  - [R detection (version 2)](https://www.kaggle.com/models/abdessamiguebli/r-detection)
  - [Beat Classification](https://www.kaggle.com/models/abdessamiguebli/ecg-beat-classification-model)
  - [Signal Classification](https://www.kaggle.com/models/abdessamiguebli/ecg-signal-classification)

5. **Register models to ML-Flow**

first run ml-flow server

```bash
mlflow server --host 127.0.0.1 --port 8080
```

then run the registration script

```bash
python register_models.py
```

## 2. **Run the server**

Finally, run the servers with the following command:

```bash
spade run
```

```bash
mlflow server --host 127.0.0.1 --port 8080
```

```bash
python manage.py runserver
```

# full space error:

its because of full cache space , clean it using

```bash
sudo rm -rf /tmp/*
```

```bash
export TMPDIR="/media/kali/D/tmp"
mkdir -p "$TMPDIR"
```
