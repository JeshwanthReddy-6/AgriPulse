import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error

# === Load Dataset ===
df = pd.read_csv("augmented_dataset_no_region.csv")

# === Fertility Score Calculation (Refined pH Handling) ===
def fertility_score(n, p, k, ph):
    score = 0
    score += 1 if n < 280 else 2 if n <= 560 else 3
    score += 1 if p < 10 else 2 if p <= 25 else 3
    score += 1 if k < 110 else 2 if k <= 280 else 3

    # pH scoring with strong penalties
    if ph < 4.5 or ph > 9.0:
        return 3  # extreme stress → very low fertility score
    elif ph < 5.5 or ph > 8.5:
        score += 1
    elif 5.5 <= ph <= 6.5 or 7.5 <= ph <= 8.5:
        score += 2
    else:
        score += 3
    return score

# === pH Recommendation Helper ===
def ph_recommendation(ph):
    if ph < 5.5:
        return [
            f"Soil is too acidic (pH={ph:.2f}). Apply lime (CaCO₃) to raise pH.",
            "Incorporate organic compost to buffer acidity.",
            "Avoid ammonium-based fertilizers."
        ]
    elif ph > 8.5:
        return [
            f"Soil is too alkaline (pH={ph:.2f}). Use sulfur or gypsum to lower pH.",
            "Avoid excessive irrigation with alkaline water.",
            "Grow pH-tolerant crops (e.g., barley, cotton)."
        ]
    elif 6.5 <= ph <= 7.5:
        return [f"Soil pH is optimal ({ph:.2f}). No pH correction needed."]
    else:
        return [f"Soil pH ({ph:.2f}) is moderately acidic/alkaline. Monitor crop performance and adjust as needed."]

# === Add Derived Features ===
df["FertilityScore"] = df.apply(lambda row: fertility_score(row["N"], row["P"], row["K"], row["pH"]), axis=1)
df["NPK_sum"] = df["N"] + df["P"] + df["K"]
df["N_per_Temp"] = df["N"] / (df["Temperature"] + 1)
df["Rainfall_per_K"] = df["Rainfall"] / (df["K"] + 1)

# === One-hot Encoding ===
df_encoded = pd.get_dummies(df, columns=["Crop", "PreviousCrop"])

# === Train Remark Classifier ===
X_remark = df_encoded.drop(["Yield", "Remark"], axis=1)
y_remark = df["Remark"]
Xr_train, Xr_test, yr_train, yr_test = train_test_split(X_remark, y_remark, test_size=0.2, random_state=42)

remark_model = RandomForestClassifier(n_estimators=100, random_state=42)
remark_model.fit(Xr_train, yr_train)

#print("\n=== Remark Classification Report ===")
yr_pred = remark_model.predict(Xr_test)
#print(classification_report(yr_test, yr_pred))

# === Train Yield Regressor ===
df_encoded["PredictedRemark"] = remark_model.predict(X_remark)
df_encoded["PredictedRemark"] = df_encoded["PredictedRemark"].apply(lambda x: 1 if x == "normal" else 0)

X_yield = df_encoded.drop(["Yield", "Remark"], axis=1)
y_yield = df["Yield"]
Xy_train, Xy_test, yy_train, yy_test = train_test_split(X_yield, y_yield, test_size=0.2, random_state=42)

yield_model = RandomForestRegressor(n_estimators=200, random_state=42)
yield_model.fit(Xy_train, yy_train)

yy_pred = yield_model.predict(Xy_test)
#print("\n=== Yield Prediction Summary ===")
#print(f"Min Yield: {int(min(yy_pred))} kg/ha")
#print(f"Max Yield: {int(max(yy_pred))} kg/ha")
#print(f"Avg Yield: {int(sum(yy_pred) / len(yy_pred))} kg/ha")
#print(f"Mean Absolute Error: {mean_absolute_error(yy_test, yy_pred):.2f}")

# === Crop Baseline Yields (example values) ===
DATASET_AVG_YIELD = 1645
crop_baseline = {"Rice": 4000, "Wheat": 3500, "Cotton": 2500, "Maize": 5000, "Soybean": 2800}
crop_caps = {"Rice": 9000, "Wheat": 8000, "Maize": 8500, "Cotton": 6000, "Soybean": 5000}

# === Recommended NPK values (kg/ha) ===
recommended_npk = {
    "Rice": {"N": 150, "P": 60, "K": 40},
    "Wheat": {"N": 120, "P": 60, "K": 40},
    "Maize": {"N": 150, "P": 75, "K": 40},
    "Cotton": {"N": 100, "P": 50, "K": 50},
    "Soybean": {"N": 20, "P": 60, "K": 40},
    "Potato": {"N": 180, "P": 60, "K": 100},
    "Tomato": {"N": 150, "P": 75, "K": 75},
    "Onion": {"N": 100, "P": 50, "K": 50},
    "Banana": {"N": 200, "P": 60, "K": 200},
    "Groundnut": {"N": 25, "P": 50, "K": 75},
    "Sugarcane": {"N": 250, "P": 115, "K": 115},
    "Sorghum": {"N": 100, "P": 50, "K": 40},
    "Millet": {"N": 80, "P": 40, "K": 40},
    "Pigeon Pea": {"N": 20, "P": 60, "K": 40},
    "Chickpea": {"N": 20, "P": 50, "K": 40},
    "Mustard": {"N": 120, "P": 60, "K": 40},
    "Lentil": {"N": 20, "P": 40, "K": 30},
    "Barley": {"N": 80, "P": 40, "K": 40}
}

# === Crop optimal ranges for temp, pH, rainfall ===
crop_optimal = {
    "wheat": {"temp_min": 10, "temp_max": 30, "ph_min": 6.0, "ph_max": 7.5, "rain_min": 300, "rain_max": 900},
    "rice": {"temp_min": 20, "temp_max": 35, "ph_min": 5.0, "ph_max": 7.0, "rain_min": 1000, "rain_max": 2000},
    "maize": {"temp_min": 18, "temp_max": 32, "ph_min": 5.5, "ph_max": 7.5, "rain_min": 500, "rain_max": 800},
    "cotton": {"temp_min": 20, "temp_max": 35, "ph_min": 5.5, "ph_max": 7.5, "rain_min": 500, "rain_max": 1200},
    "soybean": {"temp_min": 18, "temp_max": 32, "ph_min": 5.5, "ph_max": 7.5, "rain_min": 700, "rain_max": 1000},
    "potato": {"temp_min": 15, "temp_max": 25, "ph_min": 5.0, "ph_max": 6.5, "rain_min": 500, "rain_max": 700},
    "groundnut": {"temp_min": 20, "temp_max": 30, "ph_min": 5.5, "ph_max": 7.0, "rain_min": 500, "rain_max": 1000},
    "sugarcane": {"temp_min": 20, "temp_max": 38, "ph_min": 6.0, "ph_max": 8.0, "rain_min": 1200, "rain_max": 1500},
    "sorghum": {"temp_min": 25, "temp_max": 35, "ph_min": 5.5, "ph_max": 7.5, "rain_min": 400, "rain_max": 800},
    "millet": {"temp_min": 25, "temp_max": 35, "ph_min": 5.0, "ph_max": 7.5, "rain_min": 300, "rain_max": 500},
    "pigeon pea": {"temp_min": 18, "temp_max": 30, "ph_min": 5.0, "ph_max": 7.0, "rain_min": 600, "rain_max": 1000},
    "chickpea": {"temp_min": 10, "temp_max": 30, "ph_min": 6.0, "ph_max": 7.5, "rain_min": 400, "rain_max": 600},
    "mustard": {"temp_min": 10, "temp_max": 25, "ph_min": 6.0, "ph_max": 7.5, "rain_min": 350, "rain_max": 550},
    "lentil": {"temp_min": 10, "temp_max": 25, "ph_min": 6.0, "ph_max": 7.5, "rain_min": 300, "rain_max": 450},
    "barley": {"temp_min": 12, "temp_max": 25, "ph_min": 6.0, "ph_max": 7.5, "rain_min": 300, "rain_max": 500},
}

# === Rainfall Factor ===
def rainfall_factor(crop, rainfall):
    crop = crop.lower()
    if crop not in crop_optimal:
        return 1.0
    rmin, rmax = crop_optimal[crop]["rain_min"], crop_optimal[crop]["rain_max"]
    if rainfall < rmin:
        return rainfall / rmin
    elif rainfall > rmax:
        return rmax / rainfall
    else:
        return 1.0

# === Yield Adjustment with Crop, pH, Temp, Rainfall ===
def adjust_yield(predicted_yield, crop_name, ph, temperature, rainfall):
    crop_key = crop_name.title()
    crop_factor = crop_baseline.get(crop_key, DATASET_AVG_YIELD) / DATASET_AVG_YIELD
    adjusted = predicted_yield * crop_factor

    # pH stress
    if ph < 4.5 or ph > 9:
        ph_factor = 0.03 if ph < 4.5 else 0.05
    elif ph < 5.5 or ph > 8.5:
        ph_factor = 0.5
    elif ph < 6.0 or ph > 8.0:
        ph_factor = 0.8
    else:
        ph_factor = 1.0
    adjusted *= ph_factor

    # Temperature stress
    opt = crop_optimal.get(crop_name.lower(), {"temp_min": 20, "temp_max": 30})
    tmin, tmax = opt["temp_min"], opt["temp_max"]
    if temperature < tmin:
        temp_factor = 0.9 if temperature >= tmin - 2 else 0.7
    elif temperature > tmax:
        delta = temperature - tmax
        if delta <= 2: temp_factor = 0.8
        elif delta <= 5: temp_factor = 0.6
        else: temp_factor = 0.4
    else:
        temp_factor = 1.0
    adjusted *= temp_factor

    # Rainfall stress
    rf = rainfall_factor(crop_name, rainfall)
    adjusted *= rf

    # Clamp to crop cap
    adjusted = max(0, min(adjusted, crop_caps.get(crop_key, 10000)))
    return round(predicted_yield, 2), crop_factor, ph_factor, temp_factor, rf, round(adjusted, 2)

# === Fertilizer Recommendation per crop ===
def fertilizer_recommendation(crop, N, P, K, ph, fertility_score_val):
    crop = crop.title()
    ideal = recommended_npk.get(crop, {"N": 100, "P": 50, "K": 50})

    add_N = max(0, round(ideal["N"] - N))
    add_P = max(0, round(ideal["P"] - P))
    add_K = max(0, round(ideal["K"] - K))

    recs = [
        f"Apply additional Nitrogen (N): {add_N} kg/ha",
        f"Apply additional Phosphorus (P₂O₅): {add_P} kg/ha",
        f"Apply additional Potassium (K₂O): {add_K} kg/ha"
    ]

    if fertility_score_val <= 6:
        recs.extend(["Apply organic compost", "Use green manure (e.g., Dhaincha)", "Add biofertilizers with FYM"])
    elif fertility_score_val <= 9:
        recs.extend(["Apply balanced NPK (20:20:0)", "Incorporate green manure before sowing"])
    else:
        recs.extend(["Maintain current fertilization routine", "Use micronutrients only if deficiencies appear"])

    recs.extend(ph_recommendation(ph))
    return recs

# === Prediction Function ===
def predict_from_input(user_input):
    user_input["FertilityScore"] = fertility_score(user_input["N"], user_input["P"], user_input["K"], user_input["pH"])
    user_input["NPK_sum"] = user_input["N"] + user_input["P"] + user_input["K"]
    user_input["N_per_Temp"] = user_input["N"] / (user_input["Temperature"] + 1)
    user_input["Rainfall_per_K"] = user_input["Rainfall"] / (user_input["K"] + 1)

    df_input = pd.DataFrame([user_input])
    df_input_encoded = pd.get_dummies(df_input)

    for col in X_remark.columns:
        if col not in df_input_encoded.columns:
            df_input_encoded[col] = 0
    df_input_encoded = df_input_encoded[X_remark.columns]

    predicted_remark = remark_model.predict(df_input_encoded)[0]
    predicted_remark_numeric = 1 if predicted_remark == "normal" else 0

    df_input_encoded["PredictedRemark"] = predicted_remark_numeric

    for col in X_yield.columns:
        if col not in df_input_encoded.columns:
            df_input_encoded[col] = 0
    df_input_encoded = df_input_encoded[X_yield.columns]

    predicted_yield = yield_model.predict(df_input_encoded)[0]
    raw_yield, crop_factor, ph_factor, temp_factor, rain_factor, adjusted_yield = adjust_yield(
        predicted_yield, user_input["Crop"], user_input["pH"], user_input["Temperature"], user_input["Rainfall"]
    )

    # === Final remark override based on adjusted yield ===
    if adjusted_yield < 0.4 * DATASET_AVG_YIELD:
        predicted_remark = "crop failure"
    elif adjusted_yield < 0.7 * DATASET_AVG_YIELD:
        predicted_remark = "crop faliure"
    else:
        predicted_remark = "normal"

    recs = fertilizer_recommendation(
        user_input["Crop"], user_input["N"], user_input["P"], user_input["K"], user_input["pH"], user_input["FertilityScore"]
    )

    return {
        "Soil Fertility Score": user_input["FertilityScore"],
        "Predicted Remark": predicted_remark,
        "Raw Yield (kg/ha)": raw_yield,
        "Crop Factor": crop_factor,
        "pH Factor": ph_factor,
        "Temperature Factor": temp_factor,
        "Rainfall Factor": rain_factor,
        "Final Adjusted Yield (kg/ha)": adjusted_yield,
        "Recommendations": recs
    }

# === Run Prediction ===
if __name__ == "__main__":
    print("=== Enter Input Values ===")
    N = int(input("Enter Nitrogen level (N): "))
    P = int(input("Enter Phosphorus level (P): "))
    K = int(input("Enter Potassium level (K): "))
    pH = float(input("Enter soil pH: "))
    Temperature = float(input("Enter Temperature (°C): "))
    Rainfall = float(input("Enter Rainfall (mm): "))
    Crop = input("Enter Crop name: ").strip().title()
    PreviousCrop = input("Enter Previous Crop : ").strip().title()

    user_input = {
        "N": N, "P": P, "K": K, "pH": pH,
        "Temperature": Temperature, "Rainfall": Rainfall,
        "Crop": Crop, "PreviousCrop": PreviousCrop
    }

    result = predict_from_input(user_input)

    print("\n=== Prediction Result ===")
    print(f"Soil Fertility Score: {result['Soil Fertility Score']}")
    print(f"Predicted Remark: {result['Predicted Remark']}")
    print(f"Predicted Yield: {result['Final Adjusted Yield (kg/ha)']} kg/ha")
    print("Recommendations:")
    for rec in result["Recommendations"]:
        print(f"- {rec}")
