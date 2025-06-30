# ECG-classification-BackEnd
for more details , check [my portfolio](https://ab2gbl-portfolio.vercel.app/work/AI-agents-for-real-time-ECG-interpretation)

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
python -m venv myenv # python 3.12
```

- For Linux:

```bash
python3 -m venv myenv   # python 3.12
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
  - [CNN-LSTM](https://www.kaggle.com/models/abdessamiguebli/cnn-lstm-for-ecg-mask-detection)
  - [TCN](https://www.kaggle.com/models/abdessamiguebli/tcn-model-for-ecg-mask-detection)
  - [UNet](https://www.kaggle.com/models/abdessamiguebli/unet-model-for-ecg-mask-detection)
  - [R detection (version 2)](https://www.kaggle.com/models/abdessamiguebli/r-detection)
  - [Beat Classification](https://www.kaggle.com/models/abdessamiguebli/ecg-beat-classification/)
  - [Signal Classification](https://www.kaggle.com/models/abdessamiguebli/ecg-full-signal-classification)
  - [Other diseases](https://www.kaggle.com/models/abdessamiguebli/other-diseases-models) put it in `models/others/`

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
mlflow server --host 127.0.0.1 --port 8080 # if you didnt start it yet
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
