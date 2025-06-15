import subprocess

print("Registering models...")
subprocess.run(["python", "acquisition/agents/ml_flow/signal_normality_model_register.py"])
print("Signal_normality model registered successfully.")
subprocess.run(["python", "acquisition/agents/ml_flow/signal_SB_model_register.py"])
print("Signal_SB model registered successfully.")
