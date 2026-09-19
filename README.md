# 🚗 Smart Parking Occupancy Prediction

An end-to-end machine learning system that predicts real-time parking spot occupancy using IIoT sensor data, temporal patterns, and environmental factors — deployed as an interactive Streamlit web application.

---

## 📌 Overview

Urban parking inefficiency contributes significantly to traffic congestion, fuel wastage, and driver frustration. This project addresses that problem by building a classification model that predicts whether a given parking spot is **Occupied** or **Vacant**, based on sensor readings, time-based patterns, and contextual features such as vehicle type, weather, and traffic conditions.

The system is built in two parts:
1. **A full ML pipeline** (data cleaning → EDA → feature engineering → model training → evaluation) developed in Jupyter Notebook.
2. **A deployed Streamlit web app** that lets users log in, check real-time predicted availability for a spot, and view their prediction history.

---

## 🎯 Business Understanding

Smart parking systems help reduce:
- Traffic congestion caused by vehicles searching for parking
- Fuel wastage and unnecessary vehicle movement
- Driver waiting time and frustration

This project predicts parking occupancy using IIoT sensor data and temporal machine learning features to support:
- Intelligent parking allocation
- Real-time parking analytics
- Parking guidance systems
- Smart city infrastructure development

---

## 🧠 Machine Learning Pipeline

The notebook (`notebooks/main.ipynb`) follows a structured, production-style ML workflow:

### 1. Data Loading & Inspection
Dataset dimensions, feature types, missing values, target distribution, and categorical/numerical breakdown are reviewed to catch data quality issues early.

### 2. Data Cleaning
- Timestamp conversion and datatype correction
- Duplicate checking
- Sensor value validation
- Target label encoding

### 3. Exploratory Data Analysis (EDA)
In-depth analysis across five dimensions:

| Analysis | Insight |
|---|---|
| **Occupancy Overview** | Balanced distribution between occupied and vacant states, reducing model bias risk |
| **Temporal Patterns** | Occupancy is higher during daytime working hours and on weekdays vs. weekends/late-night |
| **Sensor Analysis** | Proximity, pressure, and ultrasonic sensor readings show clear separation between occupied and vacant spots |
| **External Factors** | Traffic level, vehicle type, parking zone, and weather all influence occupancy behavior |
| **Correlation Matrix** | Temporal and sensor-based features show moderate correlation with occupancy status |

### 4. Feature Engineering
- **Temporal features** — hour of day, weekday/weekend, peak traffic windows
- **Cyclical encoding** — sine/cosine transforms for hour, day, and month to preserve circular time relationships
- **Lag features** — previous occupancy states to capture continuity patterns
- **Derived sensor features** — combined/averaged sensor signals for stronger representation
- **One-hot encoding** — categorical variables (vehicle type, user type, zone, spot size, payment status, traffic level)

### 5. Model Training
Three classification models were trained and compared using a stratified train-test split, feature scaling, and cross-validation:
- **Logistic Regression**
- **Random Forest**
- **XGBoost**

### 6. Model Evaluation
Models were evaluated using:
- Accuracy, Precision, Recall, F1-Score
- ROC-AUC and Precision-Recall curves
- Confusion matrices
- Feature importance analysis

**Key finding:** Historical occupancy patterns and sensor readings contribute most to prediction performance, confirming that temporal continuity and IIoT sensor signals are the primary drivers of accurate occupancy classification.

---

## 💡 Key Business Insights

1. Historical occupancy patterns are strong indicators of future occupancy.
2. Sensor readings provide reliable evidence of parking spot usage.
3. Parking demand varies significantly across different times of the day.
4. Traffic conditions influence parking occupancy behavior across zones.

---

## 🖥️ Application Features

The deployed Streamlit app translates the trained model into a usable, end-user-facing product:

- **🔐 Sign In** — lightweight session-based login for a personalized experience
- **🔮 Predict Occupancy** — users select time, vehicle type, and location details to get an instant Vacant/Occupied prediction with a confidence score
- **🕓 History** — a running log of the user's prediction checks during their session
- **🎨 Custom UI** — dark theme, card-based layout, and a custom-designed vector logo for a polished, production-like feel

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data Processing | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine Learning | Scikit-learn, XGBoost |
| Model Persistence | Pickle |
| Web App | Streamlit |
| Language | Python 3.13 |

---

## 📊 Sample Visualizations

The `outputs/` folder contains the full set of EDA and evaluation visualizations generated by the notebook, including occupancy distribution, temporal trend charts, sensor analysis, correlation matrices, confusion matrices, ROC/PR curves, and feature importance rankings.

---

## 🔮 Future Enhancements

- Real-time IoT sensor integration (live data feed instead of static/synthetic dataset)
- Cloud deployment with a live occupancy dashboard
- User authentication with persistent accounts
- Multi-lot support with map-based spot visualization
- Model retraining pipeline on real-world parking sensor datasets (e.g., Birmingham Parking Occupancy dataset)

---

## 📄 License

This project is open-source and available for educational and research purposes.

---

## 🙋 Author

Built as part of a Smart Parking IIoT capstone project applying machine learning to real-world urban infrastructure challenges.
